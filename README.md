# FaceSync: Smart Staff Attendance Tracker

FaceSync is a Streamlit-based staff attendance system that uses face recognition for punch in/out, applies configurable attendance rules, and supports alerting through Email, SMS, and WhatsApp.

## Current Capabilities

- Face-based staff registration and attendance marking
- Attendance state engine with Grace, Late, Permission, Half-Day and Punch-In-Over logic
- Monthly counters for Grace/Late/Permission usage
- Daily and staff-wise report views
- Admin tools for staff management, attendance corrections, and custom alert dispatch
- Scheduled alert jobs with calendar-based enable/disable control

## Tech Stack

- Python 3.12+
- Streamlit (multi-page app)
- SQLite
- DeepFace (Facenet512) + NumPy + OpenCV Headless
- Twilio (optional: SMS/WhatsApp)
- SMTP (optional: email alerts)

## Project Layout

```text
FaceSync/
├── app.py
├── alerts.py
├── attendance_logic.py
├── config.py
├── database.py
├── face_utils.py
├── services.py
├── ui.py
├── pages/
│   ├── 1_Register.py
│   ├── 2_Mark_Attendance.py
│   ├── 3_Reports.py
│   └── 4_Admin.py
├── .env.example
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Quick Start

1. Clone the repository.
2. Install dependencies:

```bash
uv sync
# or
pip install -r requirements.txt
```

3. Create environment file:

```bash
cp .env.example .env
```

4. Update `.env` values for your environment.
5. (Optional) Initialize schema explicitly:

```bash
python database.py
```

6. Run the app:

```bash
uv run streamlit run app.py
# or
streamlit run app.py
```

## Authentication

Two authentication layers are used:

- App login (main entry): `APP_USERNAME`, `APP_PASSWORD`
- Admin panel login: `ADMIN_PASSWORD`

No passwords are hardcoded in source files. Set credentials only in your local `.env`.

## Environment Variables

Key variables (see `.env.example` for full list):

- Database: `DB_FILE` (or `DB_NAME` fallback)
- App login: `APP_USERNAME`, `APP_PASSWORD`
- Admin: `ADMIN_PASSWORD`, `ADMIN_EMAIL`, `ADMIN_PHONE`
- Email: `EMAIL_SMTP_SERVER`, `EMAIL_SMTP_PORT`, `EMAIL_USER`, `EMAIL_PASSWORD`, `EMAIL_FROM_NAME`
- Twilio: `TWILIO_SID`, `TWILIO_TOKEN`, `TWILIO_PHONE_NUMBER`, `TWILIO_WHATSAPP_NUMBER`
- Alert platform toggles: `ENABLE_EMAIL_ALERTS`, `ENABLE_SMS_ALERTS`, `ENABLE_WHATSAPP_ALERTS`
- Alert calendar file: `ALERT_CALENDAR_CSV`

## Attendance Windows (Current Rules)

Punch-in windows:

- 07:00-08:00: `Present`
- 08:01-08:05: `Present (Grace)` if available, then fallback to Late/Permission/Half Day
- 08:06-08:10: `Late` if available, then fallback to Permission/Half Day
- 08:11-09:00: `Permission` if available, else `Half Day Leave - Forenoon`
- 09:01-10:50: `Half Day Leave - Forenoon`
- After 10:50: `Punch In Time Over - Full day leave` (no record is created)

Punch-out windows:

- 10:30-12:29: `Half Day Leave - Afternoon`
- 12:30-17:55: `Present`
- After 17:55: `Half Day Leave - Afternoon`
- Earlier than valid windows: `Early Leave`

Monthly limits:

- Grace: 5
- Late: 2
- Permission: 2

## Scheduled Alerts

Configured jobs:

- 07:55 -> absent check
- 12:25 -> pending punch-out check
- 18:00 -> end-of-day summary

Jobs run only when the date has `STATUS=1` in the calendar CSV referenced by `ALERT_CALENDAR_CSV`.

## Alerts

Supported channels:

- Email (SMTP)
- SMS (Twilio)
- WhatsApp (Twilio)

You can test channel configuration with:

```bash
python alerts.py
```

## Engineering Notes

- Keep `.env` out of version control.
- Replace default credentials before deployment.
- Use absolute or project-relative path for `ALERT_CALENDAR_CSV`.
- Avoid creating local files named after Python stdlib modules (for example `csv.py`) to prevent import shadowing issues.
- Streamlit Cloud OpenCV fix: this repo includes `packages.txt` (`libgl1`, `libglib2.0-0`) to satisfy DeepFace/cv2 native dependencies.

## License

MIT License.
