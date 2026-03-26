# FaceSync: Smart Staff Attendance Tracker

A zero-cost, face recognition-based attendance system built with Python, Streamlit, and DeepFace.

## Features

- **Face Recognition Integration**: Register and punch in/out using facial features
- **Attendance Rules**: Automatic calculation of Late, Grace, Permission, and Half-Day status
- **Monthly Counters**: Tracks limits for grace periods and permissions
- **Reporting**: Daily logs and individual staff history
- **Multi-Platform Alerts**: Automated notifications via Email, SMS, and WhatsApp
- **Scheduled Reminders**: Background jobs for attendance reminders and daily reports
- **Admin Panel**: Manual overrides and staff management

## Tech Stack

- **Frontend**: Streamlit
- **Backend Logic**: Python
- **Database**: SQLite3
- **Face Recognition**: DeepFace (Facenet512) + OpenCV
- **Email**: SMTP (Gmail compatible)
- **SMS/WhatsApp**: Twilio API
- **Package Management**: UV

## Installation

1. **Clone the repository**

2. **Install dependencies using uv**
   ```bash
   uv sync
   # OR
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Initialize the Database**
   ```bash
   python database.py
   ```
   *Note: The app initializes the DB automatically on first run, but running the script ensures schema creation.*

## Usage

1. **Run the Application**
   ```bash
   uv run streamlit run app.py
   ```
2. **Navigate to "Register"** to add staff members
3. **Navigate to "Mark Attendance"** to punch in/out
4. **View "Reports"** for analytics

---

## 📢 Alert System

The system includes a comprehensive alert module that sends notifications via **Email**, **SMS**, and **WhatsApp**.

### Supported Platforms

| Platform | Provider | Configuration |
|----------|----------|---------------|
| 📧 Email | SMTP (Gmail) | `EMAIL_USER`, `EMAIL_PASSWORD` |
| 📱 SMS | Twilio | `TWILIO_SID`, `TWILIO_TOKEN`, `TWILIO_PHONE_NUMBER` |
| 💬 WhatsApp | Twilio | `TWILIO_SID`, `TWILIO_TOKEN`, `TWILIO_WHATSAPP_NUMBER` |

### Scheduled Jobs

| Time | Job | Description |
|------|-----|-------------|
| 07:55 AM | Absent Check | Reminds staff who haven't punched in |
| 12:25 PM | Out-Punch Check | Reminds staff who haven't punched out |
| 06:00 PM | Daily Report | Sends attendance summary to admin |

### Alert Configuration

Edit your `.env` file to enable/disable alert platforms:

```env
# Enable/Disable Platforms
ENABLE_EMAIL_ALERTS=true
ENABLE_SMS_ALERTS=false
ENABLE_WHATSAPP_ALERTS=false
```

### Email Setup (Gmail)

1. Enable 2-Factor Authentication on your Google account
2. Generate an [App Password](https://support.google.com/accounts/answer/185833)
3. Configure in `.env`:
   ```env
   EMAIL_SMTP_SERVER=smtp.gmail.com
   EMAIL_SMTP_PORT=587
   EMAIL_USER=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   EMAIL_FROM_NAME=FaceSync
   ```

### Twilio Setup (SMS & WhatsApp)

1. Create a [Twilio account](https://www.twilio.com/try-twilio)
2. Get your Account SID and Auth Token from the [Twilio Console](https://console.twilio.com)
3. For SMS: Purchase a phone number
4. For WhatsApp: Set up the [WhatsApp Sandbox](https://www.twilio.com/docs/whatsapp/sandbox) or apply for WhatsApp Business API
5. Configure in `.env`:
   ```env
   TWILIO_SID=your_account_sid
   TWILIO_TOKEN=your_auth_token
   TWILIO_PHONE_NUMBER=+1234567890
   TWILIO_WHATSAPP_NUMBER=+14155238886
   ```

### Testing Alerts

Run the alerts module directly to test your configuration:

```bash
python alerts.py
```

This will check which platforms are configured and display the status.

### Programmatic Usage

```python
from alerts import send_alert, send_custom_alert

# Send alert via all configured platforms
send_alert(
    message="Meeting in 10 minutes!",
    recipients=["staff@example.com"],
    subject="Meeting Reminder",
    phone_numbers=["+919876543210"]
)

# Send to specific staff members by ID
send_custom_alert(
    staff_ids=["EMP001", "EMP002"],
    message="Please check in at HR",
    subject="HR Notice"
)
```

---

## Deployment (Streamlit Community Cloud)

1. Push code to GitHub
2. Connect Streamlit Cloud to the repo
3. Add `requirements.txt`
4. Create secrets in Streamlit dashboard:
   ```toml
   # .streamlit/secrets.toml format
   EMAIL_USER = "your_email@gmail.com"
   EMAIL_PASSWORD = "your_app_password"
   TWILIO_SID = "your_sid"
   TWILIO_TOKEN = "your_token"
   ```
5. Deploy!

## Configuration

| File | Purpose |
|------|---------|
| `.env.example` | Template for environment variables |
| `attendance_logic.py` | Attendance rules (grace period, late threshold, etc.) |
| `alerts.py` | Alert timing and message templates |

## Project Structure

```
Staff-Attendance-Manager/
├── app.py                 # Main Streamlit application
├── alerts.py              # Alert system (Email/SMS/WhatsApp)
├── attendance_logic.py    # Business rules for attendance
├── database.py            # SQLite database operations
├── face_utils.py          # Face recognition utilities
├── main.py                # Entry point
├── pages/                 # Streamlit multi-page app
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## License

MIT License - Feel free to use and modify for your organization.
