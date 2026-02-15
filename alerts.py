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
from dotenv import load_dotenv
import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =====================================================
# Email Alert Function
# =====================================================


def send_email_alert(subject: str, message: str, recipients: list) -> dict:
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
                    <p>{message}</p>
                    <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from the Staff Attendance System.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Attach both plain text and HTML versions
        msg.attach(MIMEText(message, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        # Connect to SMTP server and send
        with smtplib.SMTP(config.EMAIL_SMTP_SERVER, config.EMAIL_SMTP_PORT) as server:
            server.starttls()  # Enable TLS encryption
            server.login(config.EMAIL_USER, config.EMAIL_PASSWORD)
            server.sendmail(config.EMAIL_USER, recipients, msg.as_string())

        logger.info(f"Email sent successfully to {len(recipients)} recipient(s)")
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


def send_sms_alert(message: str, phone_numbers: list) -> dict:
    """
    Send an SMS alert via Twilio to the specified phone numbers.

    Args:
        message: SMS message content (max 1600 characters)
        phone_numbers: List of phone numbers in E.164 format (e.g., +1234567890)

    Returns:
        dict with 'success' boolean, 'message' string, and 'results' list
    """
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
                    body=message, from_=config.TWILIO_PHONE_NUMBER, to=clean_phone
                )

                results.append({"phone": clean_phone, "status": "sent", "sid": sms.sid})
                success_count += 1
                logger.info(f"SMS sent to {clean_phone}, SID: {sms.sid}")

            except Exception as e:
                results.append({"phone": phone, "status": "failed", "error": str(e)})
                logger.error(f"Failed to send SMS to {phone}: {str(e)}")

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


def send_whatsapp_alert(message: str, phone_numbers: list) -> dict:
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
                    body=message, from_=whatsapp_from, to=whatsapp_to
                )

                results.append(
                    {"phone": clean_phone, "status": "sent", "sid": wa_message.sid}
                )
                success_count += 1
                logger.info(
                    f"WhatsApp message sent to {clean_phone}, SID: {wa_message.sid}"
                )

            except Exception as e:
                results.append({"phone": phone, "status": "failed", "error": str(e)})
                logger.error(f"Failed to send WhatsApp to {phone}: {str(e)}")

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
        "timestamp": datetime.now().isoformat(),
        "message": message,
        "platforms": {},
    }

    # Determine which platforms to use
    if platforms is None:
        platforms = []
        if ENABLE_EMAIL_ALERTS:
            platforms.append("email")
        if ENABLE_SMS_ALERTS:
            platforms.append("sms")
        if ENABLE_WHATSAPP_ALERTS:
            platforms.append("whatsapp")

    # Send via Email
    if "email" in platforms and recipients:
        results["platforms"]["email"] = send_email_alert(subject, message, recipients)

    # Send via SMS
    if "sms" in platforms and phone_numbers:
        results["platforms"]["sms"] = send_sms_alert(message, phone_numbers)

    # Send via WhatsApp
    if "whatsapp" in platforms and phone_numbers:
        results["platforms"]["whatsapp"] = send_whatsapp_alert(message, phone_numbers)

    # If no platforms were configured or available, log as mock
    if not results["platforms"]:
        logger.info("--- MOCK ALERT (No platforms configured) ---")
        logger.info(f"Message: {message}")
        logger.info(f"Would send to emails: {recipients}")
        logger.info(f"Would send to phones: {phone_numbers}")
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
    logger.info("Running Absent Check Job...")
    conn = database.get_connection()
    c = conn.cursor()
    today = datetime.now().date()

    try:
        # Get all staff with their contact info
        c.execute("SELECT staff_id, name, email, mobile_number FROM staff")
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
            names = [s["name"] for s in absentees]
            emails = [s["email"] for s in absentees if s["email"]]
            phones = [s["phone"] for s in absentees if s["phone"]]

            # Full message for email
            full_message = f"""⏰ Attendance Reminder

Hello! This is a friendly reminder to punch in for today ({today.strftime('%B %d, %Y')}).

Staff pending punch-in: {', '.join(names)}

Please mark your attendance as soon as possible.

Thank you!"""

            # Shorter message for SMS/WhatsApp (under 160 characters for trial accounts)
            sms_message = f"⏰ Attendance Reminder: Please punch in today ({today.strftime('%B %d, %Y')}). Pending: {', '.join(names)}"

            send_alert(
                message=full_message,
                recipients=emails,
                subject="⏰ Attendance Reminder - Please Punch In",
                phone_numbers=phones,
                platforms=(
                    ["email", "sms", "whatsapp"]
                    if config.ENABLE_SMS_ALERTS or config.ENABLE_WHATSAPP_ALERTS
                    else ["email"]
                ),
            )

            # Send shorter SMS separately if needed
            if phones and (config.ENABLE_SMS_ALERTS or config.ENABLE_WHATSAPP_ALERTS):
                if config.ENABLE_SMS_ALERTS:
                    send_sms_alert(sms_message, phones)
                if config.ENABLE_WHATSAPP_ALERTS:
                    send_whatsapp_alert(sms_message, phones)

            logger.info(f"Sent absent check alerts to {len(absentees)} staff member(s)")
        else:
            logger.info("All staff have punched in. No alerts needed.")

    except Exception as e:
        logger.error(f"Error in absent check job: {str(e)}")
    finally:
        conn.close()


def job_out_punch_check():
    """
    Run at 12:45 PM. Check who hasn't punched out.
    Useful for half-day tracking or lunch break reminders.
    """
    logger.info("Running Out Punch Check Job...")
    conn = database.get_connection()
    c = conn.cursor()
    today = datetime.now().date()

    try:
        # Get staff who punched in but haven't punched out
        c.execute(
            """
            SELECT a.staff_id, s.name, s.email, s.mobile_number, a.in_time
            FROM attendance a
            JOIN staff s ON a.staff_id = s.staff_id
            WHERE a.punch_date = ? AND a.out_time IS NULL
        """,
            (today,),
        )

        staff_pending_out = c.fetchall()

        if staff_pending_out:
            pending_list = []
            emails = []
            phones = []

            for row in staff_pending_out:
                pending_list.append({"name": row[1], "in_time": row[4]})
                if row[2]:  # email
                    emails.append(row[2])
                if row[3]:  # phone
                    phones.append(row[3])

            names = [p["name"] for p in pending_list]

            # Full message for email
            full_message = f"""📤 Punch-Out Reminder

Hello! This is a reminder that you haven't punched out yet for today ({today.strftime('%B %d, %Y')}).

Staff pending punch-out: {', '.join(names)}

If you're leaving for half-day or lunch, please remember to punch out.

Thank you!"""

            # Shorter message for SMS/WhatsApp
            sms_message = f"📤 Punch-Out Reminder: Please punch out today ({today.strftime('%B %d, %Y')}). Pending: {', '.join(names)}"

            send_alert(
                message=full_message,
                recipients=emails,
                subject="📤 Reminder - Please Punch Out",
                phone_numbers=phones,
                platforms=(
                    ["email", "sms", "whatsapp"]
                    if config.ENABLE_SMS_ALERTS or config.ENABLE_WHATSAPP_ALERTS
                    else ["email"]
                ),
            )

            # Send shorter SMS separately if needed
            if phones and (config.ENABLE_SMS_ALERTS or config.ENABLE_WHATSAPP_ALERTS):
                if config.ENABLE_SMS_ALERTS:
                    send_sms_alert(sms_message, phones)
                if config.ENABLE_WHATSAPP_ALERTS:
                    send_whatsapp_alert(sms_message, phones)

            logger.info(
                f"Sent out-punch reminders to {len(staff_pending_out)} staff member(s)"
            )
        else:
            logger.info("No pending punch-outs found.")

    except Exception as e:
        logger.error(f"Error in out punch check job: {str(e)}")
    finally:
        conn.close()


def job_end_of_day_report():
    """
    Run at 6:00 PM. Send daily attendance summary to admins.
    """
    logger.info("Running End of Day Report Job...")
    conn = database.get_connection()
    c = conn.cursor()
    today = datetime.now().date()

    try:
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

This is an automated daily summary from the Staff Attendance System."""

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
            )
            # Send shorter SMS separately
            if phones and (config.ENABLE_SMS_ALERTS or config.ENABLE_WHATSAPP_ALERTS):
                if config.ENABLE_SMS_ALERTS:
                    send_sms_alert(sms_message, phones)
                if config.ENABLE_WHATSAPP_ALERTS:
                    send_whatsapp_alert(sms_message, phones)
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
    # Morning absent check (before work hours)
    schedule.every().day.at("07:55").do(job_absent_check)

    # Midday out-punch check
    schedule.every().day.at("12:45").do(job_out_punch_check)

    # End of day report
    schedule.every().day.at("16:00").do(job_end_of_day_report)

    logger.info("Scheduler started. Scheduled jobs:")
    logger.info("  - 07:55 AM: Absent check")
    logger.info("  - 12:45 PM: Out-punch check")
    logger.info("  - 04:00 PM: Daily report")

    while True:
        schedule.run_pending()
        time.sleep(1)  # Check every second for precise timing


def start_background_scheduler():
    """
    Start the scheduler in a background thread.
    """
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

    Args:
        staff_ids: List of staff IDs to alert
        message: Custom message content
        subject: Email subject

    Returns:
        dict with alert results
    """
    conn = database.get_connection()
    c = conn.cursor()

    try:
        # Get contact info for specified staff
        placeholders = ",".join("?" * len(staff_ids))
        c.execute(
            f"""
            SELECT staff_id, name, email, mobile_number 
            FROM staff WHERE staff_id IN ({placeholders})
        """,
            staff_ids,
        )

        staff_list = c.fetchall()

        emails = [row[2] for row in staff_list if row[2]]
        phones = [row[3] for row in staff_list if row[3]]

        return send_alert(
            message=message, recipients=emails, subject=subject, phone_numbers=phones
        )

    except Exception as e:
        logger.error(f"Error sending custom alert: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def test_alert_configuration() -> dict:
    """
    Test the alert configuration by sending a test message.

    Returns:
        dict with test results for each platform
    """
    test_message = "This is a test alert from the Staff Attendance System."
    test_subject = "🔔 Test Alert"

    results = {
        "timestamp": datetime.now().isoformat(),
        "email": None,
        "sms": None,
        "whatsapp": None,
    }

    # Test Email
    if config.EMAIL_USER and config.EMAIL_PASSWORD:
        results["email"] = send_email_alert(test_subject, test_message, [config.EMAIL_USER])
    else:
        results["email"] = {"success": False, "message": "Email not configured"}

    # Test SMS (if configured)
    if config.TWILIO_SID and config.TWILIO_TOKEN and config.TWILIO_PHONE_NUMBER and config.ADMIN_PHONE:
        results["sms"] = send_sms_alert(test_message, [config.ADMIN_PHONE])
    elif config.TWILIO_SID and config.TWILIO_TOKEN and config.TWILIO_PHONE_NUMBER:
        results["sms"] = {
            "success": True,
            "message": "SMS configured (no test phone number)",
        }
    else:
        results["sms"] = {"success": False, "message": "SMS not configured"}

    # Test WhatsApp (if configured)
    if config.TWILIO_SID and config.TWILIO_TOKEN and config.TWILIO_WHATSAPP_NUMBER and config.ADMIN_PHONE:
        results["whatsapp"] = send_whatsapp_alert(test_message, [config.ADMIN_PHONE])
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
