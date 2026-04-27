import os
import logging
import warnings
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)


def _get_bool_env(name: str, default: bool) -> bool:
	"""Parse boolean-like environment values with sensible defaults."""
	raw_value = os.getenv(name)
	if raw_value is None:
		return default
	return raw_value.strip().lower() in {"1", "true", "yes", "on"}

# Suppress TensorFlow logs and force CPU to avoid CUDA errors
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # Suppress INFO, WARNING, and ERROR logs
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# Suppress TensorFlow Python warnings
logging.getLogger("tensorflow").setLevel(logging.ERROR)
logging.getLogger("tf_keras").setLevel(logging.ERROR)

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Database
DB_FILE = os.getenv("DB_FILE", os.getenv("DB_NAME", "attendance.db")).strip()

# Face Recognition
MODEL_NAME = "Facenet512"

# Attendance Constants
TIME_START = "07:00"
TIME_GRACE_END = "08:05"
TIME_LATE_END = "08:10"
TIME_PERMISSION_END = "09:00"
TIME_HALFDAY_FN_END = "10:50"
TIME_HALFDAY_AN_END = "12:29"
TIME_FULLDAY_END = "17:55"

MAX_GRACE = 5
MAX_LATE = 2
MAX_PERMISSION = 2

# Email Configuration
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com").strip()
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER", "").strip()
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "").strip()
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "FaceSync").strip()

# Admin Configuration
ADMIN_PHONE = os.getenv("ADMIN_PHONE", "").strip()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "").strip()
APP_USERNAME = os.getenv("APP_USERNAME", "").strip()
APP_PASSWORD = os.getenv("APP_PASSWORD", "")

# Twilio Configuration
TWILIO_SID = os.getenv("TWILIO_SID", os.getenv("TWILIO_ACCOUNT_SID", "")).strip()
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN", os.getenv("TWILIO_AUTH_TOKEN", "")).strip()
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "").strip()
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "").strip()

# Alert Configuration
ENABLE_EMAIL_ALERTS = _get_bool_env("ENABLE_EMAIL_ALERTS", True)
ENABLE_SMS_ALERTS = _get_bool_env("ENABLE_SMS_ALERTS", True)
ENABLE_WHATSAPP_ALERTS = _get_bool_env("ENABLE_WHATSAPP_ALERTS", True)
ALERT_CALENDAR_CSV = os.getenv(
	"ALERT_CALENDAR_CSV", "2025-2026 (EVEN SEM).csv"
).strip()
