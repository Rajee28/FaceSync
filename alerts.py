import schedule
import time
import threading
import database
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import config

# Configure logging
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("twilio").setLevel(logging.WARNING)
logging.getLogger("twilio.http_client").setLevel(logging.WARNING)

_TWILIO_AUTH_FAILED = False
APP_URL = "https://facesync.streamlit.app/"
_CALENDAR_CACHE = {
    "path": None,
    "mtime": None,
    "status_by_date": {},
}


def _with_app_link(message: str) -> str:
    """Ensure every outgoing alert/report message includes the app URL."""
    base_message = (message or "").rstrip()
    if APP_URL in base_message:
        return base_message
    return f"{base_message}\n\nOpen FaceSync: {APP_URL}"


def _resolve_calendar_csv_path() -> str:
    """Resolve calendar CSV path from config, supporting both absolute and relative paths."""
    configured = config.ALERT_CALENDAR_CSV
    if os.path.isabs(configured):
        return configured
    return os.path.join(os.path.dirname(__file__), configured)


def _get_calendar_status_by_date() -> dict:
    """
    Load DATE->STATUS mapping from calendar CSV.

    The CSV must include DATE and STATUS columns where DATE is dd-mm-YYYY and
    STATUS uses 1 for active alert days.
    """
    path = _resolve_calendar_csv_path()

    if not os.path.exists(path):
        logger.warning("Calendar CSV not found at %s. Scheduler will not run jobs.", path)
        return {}

    mtime = os.path.getmtime(path)
    if _CALENDAR_CACHE["path"] == path and _CALENDAR_CACHE["mtime"] == mtime:
        return _CALENDAR_CACHE["status_by_date"]

    status_map = {}
    date_idx = None
    status_idx = None

    with open(path, "r", encoding="utf-8-sig") as f:
        for line_number, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line:
                continue

            columns = [col.strip() for col in line.split(",")]

            if line_number == 1:
                headers = [h.upper() for h in columns]
                try:
                    date_idx = headers.index("DATE")
                    status_idx = headers.index("STATUS")
                except ValueError:
                    logger.warning(
                        "Calendar CSV must contain DATE and STATUS headers. Scheduler will not run jobs."
                    )
                    return {}
                continue

            if date_idx is None or status_idx is None:
                continue

            if len(columns) <= max(date_idx, status_idx):
                continue

            date_str = columns[date_idx]
            status_str = columns[status_idx]

            if not date_str:
                continue

            try:
                day = datetime.strptime(date_str, "%d-%m-%Y").date()
            except ValueError:
                logger.warning(
                    "Skipping invalid DATE '%s' in calendar CSV at line %d",
                    date_str,
                    line_number,
                )
                continue

            status_map[day] = status_str

    _CALENDAR_CACHE["path"] = path
    _CALENDAR_CACHE["mtime"] = mtime
    _CALENDAR_CACHE["status_by_date"] = status_map

    return status_map


def _should_run_alert_jobs(target_date=None) -> bool:
    """Return True only when calendar STATUS for date is 1."""
    check_date = target_date or config.now_in_app_tz().date()
    status_map = _get_calendar_status_by_date()
    raw_status = status_map.get(check_date)

    if raw_status is None:
        logger.info(
            "Skipping alert jobs for %s: no DATE entry found in calendar CSV.",
            check_date,
        )
        return False

    should_run = str(raw_status).strip() == "1"
    if not should_run:
        logger.info(
            "Skipping alert jobs for %s: STATUS=%s in calendar CSV.",
            check_date,
            raw_status,
        )
    return should_run


# =====================================================
# Email Alert Function
# =====================================================


def send_email_alert(
    subject: str, message: str, recipients: list, recipient_name: str = "Unknown"
) -> dict:
    """
    Send an email alert to the specified recipients.

    Args:
        subject: Email subject line
        message: Email body content
        recipients: List of email addresses

    Returns:
        dict with 'success' boolean and 'message' string
    """
    if not config.EMAIL_USER or not config.EMAIL_PASSWORD:
        logger.warning("Email credentials not configured. Skipping email alert.")
        return {"success": False, "message": "Email credentials not configured"}

    if not recipients:
        logger.warning("No recipients provided for email alert.")
        return {"success": False, "message": "No recipients provided"}

    try:
        # Create the email message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{config.EMAIL_FROM_NAME} <{config.EMAIL_USER}>"
        msg["To"] = ", ".join(recipients)

        enriched_message = _with_app_link(message)

        # Create HTML version of the message
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 8px 8px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #888; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>📢 Attendance Alert</h2>
                </div>
                <div class="content">
                    <p>{enriched_message.replace(chr(10), '<br>')}</p>
                    <p><strong>Time:</strong> {config.now_in_app_tz().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from the FaceSync.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Attach both plain text and HTML versions
        msg.attach(MIMEText(enriched_message, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        # Connect to SMTP server and send
        with smtplib.SMTP(config.EMAIL_SMTP_SERVER, config.EMAIL_SMTP_PORT) as server:
            server.starttls()  # Enable TLS encryption
            server.login(config.EMAIL_USER, config.EMAIL_PASSWORD)
            server.sendmail(config.EMAIL_USER, recipients, msg.as_string())

        logger.info(f"Email sent successfully to {len(recipients)} recipient(s)")
        logger.info(f"Alert sent to {recipient_name} via email")
        return {
            "success": True,
            "message": f"Email sent to {len(recipients)} recipient(s)",
        }

    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed. Check email credentials.")
        return {"success": False, "message": "SMTP authentication failed"}
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {str(e)}")
        return {"success": False, "message": f"SMTP error: {str(e)}"}
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return {"success": False, "message": f"Error: {str(e)}"}


# =====================================================
# SMS Alert Function (via Twilio)
# =====================================================


def send_sms_alert(
    message: str, phone_numbers: list, recipient_name: str = "Unknown"
) -> dict:
    """
    Send an SMS alert via Twilio to the specified phone numbers.

    Args:
        message: SMS message content (max 1600 characters)
        phone_numbers: List of phone numbers in E.164 format (e.g., +1234567890)

    Returns:
        dict with 'success' boolean, 'message' string, and 'results' list
    """
    global _TWILIO_AUTH_FAILED

    if _TWILIO_AUTH_FAILED:
        return {
            "success": False,
            "message": "Twilio authentication previously failed. Skipping SMS alerts.",
            "results": [],
        }

    if not config.TWILIO_SID or not config.TWILIO_TOKEN:
        logger.warning("Twilio credentials not configured. Skipping SMS alert.")
        return {
            "success": False,
            "message": "Twilio credentials not configured",
            "results": [],
        }

    if not config.TWILIO_PHONE_NUMBER:
        logger.warning("Twilio phone number not configured. Skipping SMS alert.")
        return {
            "success": False,
            "message": "Twilio phone number not configured",
            "results": [],
        }

    if not phone_numbers:
        logger.warning("No phone numbers provided for SMS alert.")
        return {"success": False, "message": "No phone numbers provided", "results": []}

    try:
        enriched_message = _with_app_link(message)

        from twilio.rest import Client

        client = Client(config.TWILIO_SID, config.TWILIO_TOKEN)

        results = []
        success_count = 0

        for phone in phone_numbers:
            try:
                # Clean and format the phone number
                clean_phone = phone.strip()
                if not clean_phone.startswith("+"):
                    clean_phone = f"+91{clean_phone}"  # Default to India country code

                # Send the SMS
                sms = client.messages.create(
                    body=enriched_message,
                    from_=config.TWILIO_PHONE_NUMBER,
                    to=clean_phone,
                )

                results.append({"phone": clean_phone, "status": "sent", "sid": sms.sid})
                success_count += 1
                logger.info(f"SMS sent to {clean_phone}, SID: {sms.sid}")
                logger.info(f"Alert sent to {recipient_name} via sms")

            except Exception as e:
                results.append({"phone": phone, "status": "failed", "error": str(e)})
                logger.error(f"Failed to send SMS to {phone}: {str(e)}")

                # Twilio error 20003 = authentication failure.
                if "20003" in str(e) or "Authenticate" in str(e):
                    _TWILIO_AUTH_FAILED = True
                    logger.error(
                        "Twilio authentication failed. Disabling SMS/WhatsApp alerts for this run."
                    )
                    logger.error(
                        "Twilio auth diagnostics: sid_prefix=%s token_length=%s",
                        (config.TWILIO_SID[:6] + "...") if config.TWILIO_SID else "(empty)",
                        len(config.TWILIO_TOKEN) if config.TWILIO_TOKEN else 0,
                    )
                    break

        return {
            "success": success_count > 0,
            "message": f"SMS sent to {success_count}/{len(phone_numbers)} recipient(s)",
            "results": results,
        }

    except ImportError:
        logger.error("Twilio library not installed. Run: pip install twilio")
        return {
            "success": False,
            "message": "Twilio library not installed",
            "results": [],
        }
    except Exception as e:
        logger.error(f"Failed to initialize Twilio client: {str(e)}")
        return {"success": False, "message": f"Twilio error: {str(e)}", "results": []}


# =====================================================
# WhatsApp Alert Function (via Twilio)
# =====================================================


def send_whatsapp_alert(
    message: str, phone_numbers: list, recipient_name: str = "Unknown"
) -> dict:
    """
    Send a WhatsApp message via Twilio WhatsApp Business API.

    Note: Recipients must have opted in to receive WhatsApp messages from your business.
    For sandbox testing, recipients need to join your sandbox first.

    Args:
        message: WhatsApp message content
        phone_numbers: List of phone numbers in E.164 format (e.g., +1234567890)

    Returns:
        dict with 'success' boolean, 'message' string, and 'results' list
    """
    global _TWILIO_AUTH_FAILED

    if _TWILIO_AUTH_FAILED:
        return {
            "success": False,
            "message": "Twilio authentication previously failed. Skipping WhatsApp alerts.",
            "results": [],
        }

    if not config.TWILIO_SID or not config.TWILIO_TOKEN:
        logger.warning("Twilio credentials not configured. Skipping WhatsApp alert.")
        return {
            "success": False,
            "message": "Twilio credentials not configured",
            "results": [],
        }

    if not config.TWILIO_WHATSAPP_NUMBER:
        logger.warning(
            "Twilio WhatsApp number not configured. Skipping WhatsApp alert."
        )
        return {
            "success": False,
            "message": "Twilio WhatsApp number not configured",
            "results": [],
        }

    if not phone_numbers:
        logger.warning("No phone numbers provided for WhatsApp alert.")
        return {"success": False, "message": "No phone numbers provided", "results": []}

    try:
        enriched_message = _with_app_link(message)

        from twilio.rest import Client

        client = Client(config.TWILIO_SID, config.TWILIO_TOKEN)

        results = []
        success_count = 0

        # Format the WhatsApp sender number
        whatsapp_from = f"whatsapp:{config.TWILIO_WHATSAPP_NUMBER}"

        for phone in phone_numbers:
            try:
                # Clean and format the phone number
                clean_phone = phone.strip()
                if not clean_phone.startswith("+"):
                    clean_phone = f"+91{clean_phone}"  # Default to India country code

                whatsapp_to = f"whatsapp:{clean_phone}"

                # Send the WhatsApp message
                wa_message = client.messages.create(
                    body=enriched_message,
                    from_=whatsapp_from,
                    to=whatsapp_to,
                )

                results.append(
                    {"phone": clean_phone, "status": "sent", "sid": wa_message.sid}
                )
                success_count += 1
                logger.info(
                    f"WhatsApp message sent to {clean_phone}, SID: {wa_message.sid}"
                )
                logger.info(f"Alert sent to {recipient_name} via whatsapp")

            except Exception as e:
                results.append({"phone": phone, "status": "failed", "error": str(e)})
                logger.error(f"Failed to send WhatsApp to {phone}: {str(e)}")

                # Twilio error 20003 = authentication failure.
                if "20003" in str(e) or "Authenticate" in str(e):
                    _TWILIO_AUTH_FAILED = True
                    logger.error(
                        "Twilio authentication failed. Disabling SMS/WhatsApp alerts for this run."
                    )
                    logger.error(
                        "Twilio auth diagnostics: sid_prefix=%s token_length=%s",
                        (config.TWILIO_SID[:6] + "...") if config.TWILIO_SID else "(empty)",
                        len(config.TWILIO_TOKEN) if config.TWILIO_TOKEN else 0,
                    )
                    break

        return {
            "success": success_count > 0,
            "message": f"WhatsApp sent to {success_count}/{len(phone_numbers)} recipient(s)",
            "results": results,
        }

    except ImportError:
        logger.error("Twilio library not installed. Run: pip install twilio")
        return {
            "success": False,
            "message": "Twilio library not installed",
            "results": [],
        }
    except Exception as e:
        logger.error(f"Failed to initialize Twilio client: {str(e)}")
        return {"success": False, "message": f"Twilio error: {str(e)}", "results": []}


# =====================================================
# Unified Alert Function
# =====================================================


def send_alert(
    message: str,
    recipients: list,
    subject: str = "Attendance Alert",
    phone_numbers: list = None,
    platforms: list = None,
    recipient_name: str = "Unknown",
) -> dict:
    """
    Send alerts via multiple platforms (Email, SMS, WhatsApp).

    Args:
        message: Alert message content
        recipients: List of email addresses
        subject: Email subject (default: "Attendance Alert")
        phone_numbers: List of phone numbers for SMS/WhatsApp (optional)
        platforms: List of platforms to use ['email', 'sms', 'whatsapp']
                   If None, uses configured defaults

    Returns:
        dict with results from each platform
    """
    logger.info("=" * 50)
    logger.info("SENDING ALERT")
    logger.info(f"Message: {message}")
    logger.info(f"Email Recipients: {recipients}")
    logger.info(f"Phone Numbers: {phone_numbers}")
    logger.info("=" * 50)

    results = {
        "timestamp": config.now_in_app_tz().isoformat(),
        "message": message,
        "platforms": {},
    }

    # Determine which platforms to use
    if platforms is None:
        platforms = []
        if config.ENABLE_EMAIL_ALERTS:
            platforms.append("email")
        if config.ENABLE_SMS_ALERTS:
            platforms.append("sms")
        if config.ENABLE_WHATSAPP_ALERTS:
            platforms.append("whatsapp")

    # Send via Email
    if "email" in platforms and recipients:
        results["platforms"]["email"] = send_email_alert(
            subject, message, recipients, recipient_name=recipient_name
        )

    # Send via SMS
    if "sms" in platforms and phone_numbers:
        results["platforms"]["sms"] = send_sms_alert(
            message, phone_numbers, recipient_name=recipient_name
        )

    # Send via WhatsApp
    if "whatsapp" in platforms and phone_numbers:
        results["platforms"]["whatsapp"] = send_whatsapp_alert(
            message, phone_numbers, recipient_name=recipient_name
        )

    # If no platforms were configured or available, log as mock
    if not results["platforms"]:
        logger.info("--- MOCK ALERT (No platforms configured) ---")
        logger.info(f"Message: {message}")
        logger.info(f"Would send to emails: {recipients}")
        logger.info(f"Would send to phones: {phone_numbers}")
        logger.info(f"Alert sent to {recipient_name} via mock")
        logger.info("--- END MOCK ALERT ---")
        results["platforms"]["mock"] = {
            "success": True,
            "message": "Logged as mock alert",
        }

    # Determine overall success
    results["success"] = any(
        res.get("success", False) for res in results["platforms"].values()
    )

    return results


# =====================================================
# Scheduled Job Functions
# =====================================================


def job_absent_check():
    """
    Run at 7:55 AM. Check who hasn't punched in.
    Sends reminder alerts to staff who haven't marked their attendance.
    """
    if not _should_run_alert_jobs():
        return

    logger.info("Running Absent Check Job...")
    conn = database.get_connection()
    c = conn.cursor()
    today = config.now_in_app_tz().date()

    try:
        # Get all staff with their contact info
        c.execute(
            """
            SELECT staff_id, name, email, mobile_number
            FROM staff
            ORDER BY created_at DESC, id DESC
            """
        )
        all_staff = c.fetchall()

        # Get present staff for today
        c.execute("SELECT staff_id FROM attendance WHERE punch_date=?", (today,))
        present_staff_ids = [row[0] for row in c.fetchall()]

        # Find absent staff
        absentees = []
        for staff in all_staff:
            if staff[0] not in present_staff_ids:
                absentees.append(
                    {
                        "staff_id": staff[0],
                        "name": staff[1],
                        "email": staff[2],
                        "phone": staff[3],
                    }
                )

        if absentees:
            # send a personalized alert for each absent staff member
            for s in absentees:
                name = s["name"]
                email = s.get("email")
                phone = s.get("phone")

                # construct messages specific to this staff member
                full_message = f"""⏰ Attendance Reminder

Hello {name}! This is a friendly reminder to punch in for today ({today.strftime('%B %d, %Y')}).

Please mark your attendance as soon as possible.

Thank you!"""

                sms_message = (
                    f"⏰ {name}, please punch in today ({today.strftime('%B %d, %Y')})."
                )

                # email only
                if email:
                    send_alert(
                        message=full_message,
                        recipients=[email],
                        subject="⏰ Attendance Reminder - Please Punch In",
                        phone_numbers=None,
                        platforms=["email"],
                        recipient_name=name,
                    )

                # phone alerts separately with shorter text
                if phone and (
                    config.ENABLE_SMS_ALERTS or config.ENABLE_WHATSAPP_ALERTS
                ):
                    if config.ENABLE_SMS_ALERTS:
                        send_sms_alert(sms_message, [phone], recipient_name=name)
                    if config.ENABLE_WHATSAPP_ALERTS:
                        send_whatsapp_alert(
                            sms_message, [phone], recipient_name=name
                        )

            logger.info(f"Sent absent check alerts to {len(absentees)} staff member(s)")
        else:
            logger.info("All staff have punched in. No alerts needed.")

    except Exception as e:
        logger.error(f"Error in absent check job: {str(e)}")
    finally:
        conn.close()


def job_out_punch_check():
    """
    Run at 12:25 PM. Check who hasn't punched out.
    Useful for half-day tracking or lunch break reminders.
    """
    if not _should_run_alert_jobs():
        return

    logger.info("Running Out Punch Check Job...")
    conn = database.get_connection()
    c = conn.cursor()
    today = config.now_in_app_tz().date()

    try:
        # Get staff who punched in but haven't punched out
        c.execute(
            """
            SELECT a.staff_id, s.name, s.email, s.mobile_number, a.in_time
            FROM attendance a
            JOIN staff s ON a.staff_id = s.staff_id
            WHERE a.punch_date = ? AND a.out_time IS NULL
            ORDER BY s.created_at DESC, s.id DESC
        """,
            (today,),
        )

        staff_pending_out = c.fetchall()

        if staff_pending_out:
            # notify each person individually
            for row in staff_pending_out:
                name = row[1]
                email = row[2]
                phone = row[3]

                full_message = f"""📤 Punch-Out Reminder

Hello {name}! This is a reminder that you haven't punched out yet for today ({today.strftime('%B %d, %Y')}).

If you're leaving for half-day or lunch, please remember to punch out.

Thank you!"""

                sms_message = f"📤 {name}, please punch out today ({today.strftime('%B %d, %Y')})."

                if email:
                    send_alert(
                        message=full_message,
                        recipients=[email],
                        subject="📤 Reminder - Please Punch Out",
                        phone_numbers=None,
                        platforms=["email"],
                        recipient_name=name,
                    )

                if phone and (
                    config.ENABLE_SMS_ALERTS or config.ENABLE_WHATSAPP_ALERTS
                ):
                    if config.ENABLE_SMS_ALERTS:
                        send_sms_alert(sms_message, [phone], recipient_name=name)
                    if config.ENABLE_WHATSAPP_ALERTS:
                        send_whatsapp_alert(
                            sms_message, [phone], recipient_name=name
                        )

            logger.info(
                f"Sent out-punch reminders to {len(staff_pending_out)} staff member(s)"
            )
        else:
            logger.info("No pending punch-outs found.")

    except Exception as e:
        logger.error(f"Error in out punch check job: {str(e)}")
    finally:
        conn.close()


def job_end_of_day_report(force: bool = False):
    """
    Run at 6:00 PM. Send daily attendance summary to admins.

    Args:
        force: If True, bypass the 6:00 PM safety guard.
    """
    if not _should_run_alert_jobs():
        return

    logger.info("Running End of Day Report Job...")
    now = config.now_in_app_tz()
    report_hour = 18

    # Safety guard: avoid accidental early execution from manual/duplicate triggers.
    if not force and now.hour < report_hour:
        logger.warning(
            "Skipping End of Day Report: current time %s is before %02d:00",
            now.strftime("%H:%M:%S"),
            report_hour,
        )
        return

    conn = database.get_connection()
    c = conn.cursor()
    today = now.date()

    try:
        # Any staff who still have no out-punch by report time are marked as half-day afternoon.
        c.execute(
            """
            UPDATE attendance
            SET status = ?
            WHERE punch_date = ?
              AND in_time IS NOT NULL
              AND out_time IS NULL
            """,
            ("Half Day Leave - Afternoon", today),
        )
        conn.commit()

        # Get attendance summary
        c.execute("SELECT COUNT(*) FROM staff")
        total_staff = c.fetchone()[0]

        c.execute(
            """
            SELECT COUNT(DISTINCT staff_id) FROM attendance 
            WHERE punch_date = ?
        """,
            (today,),
        )
        present_count = c.fetchone()[0]

        c.execute(
            """
            SELECT COUNT(*) FROM attendance 
            WHERE punch_date = ? AND late_min > 0
        """,
            (today,),
        )
        late_count = c.fetchone()[0]

        c.execute(
            """
            SELECT COUNT(*) FROM attendance 
            WHERE punch_date = ? AND out_time IS NULL
        """,
            (today,),
        )
        pending_out = c.fetchone()[0]

        absent_count = total_staff - present_count

        # Full message for email
        full_message = f"""📊 Daily Attendance Report - {today.strftime('%B %d, %Y')}

Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Total Staff: {total_staff}
✅ Present: {present_count}
❌ Absent: {absent_count}
⏰ Late Arrivals: {late_count}
📤 Pending Punch-Out: {pending_out}
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Attendance Rate: {(present_count/total_staff*100) if total_staff > 0 else 0:.1f}%

This is an automated daily summary from the FaceSync."""

        # Shorter message for SMS/WhatsApp
        sms_message = f"📊 Daily Report {today.strftime('%Y-%m-%d')}: Present {present_count}/{total_staff}, Absent {absent_count}, Late {late_count}"

        # Send to admin email (and SMS if configured)
        admin_email = os.getenv("ADMIN_EMAIL", "")
        admin_phone = os.getenv("ADMIN_PHONE", "")
        recipients = [admin_email] if admin_email else []
        phones = [admin_phone] if admin_phone else []

        if recipients or phones:
            send_alert(
                message=full_message,
                recipients=recipients,
                subject=f"📊 Daily Attendance Report - {today.strftime('%Y-%m-%d')}",
                phone_numbers=phones,
                platforms=(
                    ["email", "sms", "whatsapp"]
                    if config.ENABLE_SMS_ALERTS or config.ENABLE_WHATSAPP_ALERTS
                    else ["email"]
                ),
                recipient_name="Admin",
            )
            # Send shorter SMS separately
            if phones and (config.ENABLE_SMS_ALERTS or config.ENABLE_WHATSAPP_ALERTS):
                if config.ENABLE_SMS_ALERTS:
                    send_sms_alert(sms_message, phones, recipient_name="Admin")
                if config.ENABLE_WHATSAPP_ALERTS:
                    send_whatsapp_alert(
                        sms_message, phones, recipient_name="Admin"
                    )
            logger.info("Daily report sent to admin")
        else:
            logger.info("Admin email/phone not configured. Daily report logged only.")
            logger.info(full_message)

    except Exception as e:
        logger.error(f"Error in end of day report job: {str(e)}")
    finally:
        conn.close()


# =====================================================
# Scheduler Functions
# =====================================================


def run_scheduler():
    """
    Main scheduler loop. Runs the scheduled jobs at specified times.
    """
    logger.info("Starting job scheduler setup...")
    config.apply_process_timezone()
    logger.info("Scheduler timezone set to %s", config.APP_TIMEZONE)

    # Morning absent check (before work hours)
    schedule.every().day.at("07:55", config.APP_TIMEZONE).do(job_absent_check)

    # Midday out-punch check
    schedule.every().day.at("12:25", config.APP_TIMEZONE).do(job_out_punch_check)

    # End of day report
    schedule.every().day.at("18:00", config.APP_TIMEZONE).do(job_end_of_day_report)

    logger.info("Job scheduler started. Scheduled jobs:")
    logger.info("  - 07:55 AM: Absent check")
    logger.info("  - 12:25 PM: Out-punch check")
    logger.info("  - 06:00 PM: Daily report")

    while True:
        schedule.run_pending()
        time.sleep(1)  # Check every second for precise timing


def start_background_scheduler():
    """
    Start the scheduler in a background thread.
    """
    logger.info("Starting background job scheduler thread...")
    t = threading.Thread(target=run_scheduler, daemon=True)
    t.start()
    logger.info("Background scheduler thread started")


# =====================================================
# Manual Alert Functions (for UI/API usage)
# =====================================================


def send_custom_alert(
    staff_ids: list, message: str, subject: str = "Custom Alert"
) -> dict:
    """
    Send a custom alert to specific staff members.

    The provided `message` may include a ``{name}`` placeholder which will be
    replaced with the recipient's name. Alerts are sent individually so that
    each staff member only sees their own name (and can even have a slightly
    different body if desired).

    Args:
        staff_ids: List of staff IDs to alert
        message: Custom message content (can contain ``{name}``)
        subject: Email subject

    Returns:
        dict with aggregated results for each staff member keyed by staff_id
    """
    if not staff_ids:
        return {
            "success": False,
            "message": "No staff IDs were provided.",
            "staff_results": {},
        }

    conn = database.get_connection()
    c = conn.cursor()

    try:
        # Get contact info for specified staff
        placeholders = ",".join("?" * len(staff_ids))
        c.execute(
            f"""
            SELECT staff_id, name, email, mobile_number 
            FROM staff WHERE staff_id IN ({placeholders})
            ORDER BY created_at DESC, id DESC
        """,
            staff_ids,
        )

        staff_list = c.fetchall()

        overall_results = {}
        for row in staff_list:
            sid, name, email, phone = row
            personalised = message.format(name=name)

            # send via email if available
            if email:
                send_alert(
                    message=personalised,
                    recipients=[email],
                    subject=subject,
                    phone_numbers=None,
                    platforms=["email"],
                    recipient_name=name,
                )

            # send via phone if available
            if phone and (config.ENABLE_SMS_ALERTS or config.ENABLE_WHATSAPP_ALERTS):
                sms_msg = personalised
                if config.ENABLE_SMS_ALERTS:
                    send_sms_alert(sms_msg, [phone], recipient_name=name)
                if config.ENABLE_WHATSAPP_ALERTS:
                    send_whatsapp_alert(sms_msg, [phone], recipient_name=name)

            overall_results[sid] = {
                "name": name,
                "email": email,
                "phone": phone,
                "status": "sent",
            }

        return {
            "success": True,
            "message": f"Alerts processed for {len(overall_results)} staff member(s).",
            "staff_results": overall_results,
        }

    except Exception as e:
        logger.error(f"Error sending custom alert: {str(e)}")
        return {
            "success": False,
            "message": "Failed to send custom alerts.",
            "error": str(e),
            "staff_results": {},
        }
    finally:
        conn.close()


def test_alert_configuration() -> dict:
    """
    Test the alert configuration by sending a test message.

    Returns:
        dict with test results for each platform
    """
    test_message = "This is a test alert from FaceSync."
    test_subject = "🔔 Test Alert"

    results = {
        "timestamp": config.now_in_app_tz().isoformat(),
        "email": None,
        "sms": None,
        "whatsapp": None,
    }

    # Test Email
    if config.EMAIL_USER and config.EMAIL_PASSWORD:
        results["email"] = send_email_alert(
            test_subject,
            test_message,
            [config.EMAIL_USER],
            recipient_name="Test Recipient",
        )
    else:
        results["email"] = {"success": False, "message": "Email not configured"}

    # Test SMS (if configured)
    if (
        config.TWILIO_SID
        and config.TWILIO_TOKEN
        and config.TWILIO_PHONE_NUMBER
        and config.ADMIN_PHONE
    ):
        results["sms"] = send_sms_alert(
            test_message, [config.ADMIN_PHONE], recipient_name="Test Recipient"
        )
    elif config.TWILIO_SID and config.TWILIO_TOKEN and config.TWILIO_PHONE_NUMBER:
        results["sms"] = {
            "success": True,
            "message": "SMS configured (no test phone number)",
        }
    else:
        results["sms"] = {"success": False, "message": "SMS not configured"}

    # Test WhatsApp (if configured)
    if (
        config.TWILIO_SID
        and config.TWILIO_TOKEN
        and config.TWILIO_WHATSAPP_NUMBER
        and config.ADMIN_PHONE
    ):
        results["whatsapp"] = send_whatsapp_alert(
            test_message, [config.ADMIN_PHONE], recipient_name="Test Recipient"
        )
    elif config.TWILIO_SID and config.TWILIO_TOKEN and config.TWILIO_WHATSAPP_NUMBER:
        results["whatsapp"] = {
            "success": True,
            "message": "WhatsApp configured (no test phone number)",
        }
    else:
        results["whatsapp"] = {"success": False, "message": "WhatsApp not configured"}

    return results


# =====================================================
# Module Entry Point
# =====================================================

if __name__ == "__main__":
    # Test the configuration
    print("Testing Alert Configuration...")
    print("-" * 50)

    config_results = test_alert_configuration()

    print(f"Email: {config_results['email']}")
    print(f"SMS: {config_results['sms']}")
    print(f"WhatsApp: {config_results['whatsapp']}")

    print("-" * 50)
    print("Configuration test complete.")
