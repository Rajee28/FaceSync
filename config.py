import os
import logging
import warnings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Suppress TensorFlow logs and force CPU to avoid CUDA errors
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # Suppress INFO, WARNING, and ERROR logs
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# Suppress TensorFlow Python warnings
logging.getLogger("tensorflow").setLevel(logging.ERROR)
logging.getLogger("tf_keras").setLevel(logging.ERROR)

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Database
DB_FILE = "attendance.db"

# Face Recognition
MODEL_NAME = "Facenet512"

# Attendance Constants
TIME_START = "07:00"
TIME_GRACE_END = "08:05"
TIME_LATE_END = "08:10"
TIME_PERMISSION_END = "09:00"
TIME_HALFDAY_FN_END = "10:30"
TIME_HALFDAY_AN_END = "12:29"
TIME_FULLDAY_END = "15:00"

MAX_GRACE = 5
MAX_LATE = 2
MAX_PERMISSION = 2

# Email Configuration
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Staff Attendance System")

# Admin Configuration
ADMIN_PHONE = os.getenv("ADMIN_PHONE", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")  # Use env var

# Twilio Configuration
TWILIO_SID = os.getenv("TWILIO_SID", "")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "")

# Alert Configuration
ENABLE_EMAIL_ALERTS = os.getenv("ENABLE_EMAIL_ALERTS", "true").lower() == "true"
ENABLE_SMS_ALERTS = os.getenv("ENABLE_SMS_ALERTS", "false").lower() == "true"
ENABLE_WHATSAPP_ALERTS = os.getenv("ENABLE_WHATSAPP_ALERTS", "false").lower() == "true"
