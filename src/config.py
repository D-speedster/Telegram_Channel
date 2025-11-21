import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- General Settings ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Telegram Bot Configuration ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in the environment variables!")

# --- Admin Configuration ---
# Get admin IDs from environment variables, split by comma, and convert to int
ADMIN_IDS_STR = os.getenv("ADMIN_USER_ID", "")
try:
    ADMIN_IDS = [int(admin_id.strip()) for admin_id in ADMIN_IDS_STR.split(',') if admin_id.strip()]
except ValueError:
    ADMIN_IDS = []
    
if not ADMIN_IDS:
    print("Warning: ADMIN_USER_ID is not set or is invalid. No admin users are configured.")

# --- Database Configuration ---
DATABASE_DIR = os.path.join(BASE_DIR, 'data', 'database')
DATABASE_PATH = os.path.join(DATABASE_DIR, 'bot.db')
os.makedirs(DATABASE_DIR, exist_ok=True) # Ensure the directory exists

# --- Banners and Media ---
BANNERS_DIR = os.path.join(BASE_DIR, 'data', 'banners')
os.makedirs(BANNERS_DIR, exist_ok=True) # Ensure the directory exists

# --- Channel Configuration ---
CHANNEL_ID = os.getenv("TARGET_CHANNEL_ID")
if not CHANNEL_ID:
    print("Warning: TARGET_CHANNEL_ID is not set. Posting to channel will fail.")

# --- Logging Configuration ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# --- Webhook Configuration (Optional) ---
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", "8443"))

# --- Bot Behavior ---
DEFAULT_REPLY_MARKUP = None # Example: ReplyKeyboardMarkup(...)
DEFAULT_PARSE_MODE = 'HTML'

# --- Banner Settings ---
# Example of how you might want to list banners
def get_banner_list():
    if not os.path.exists(BANNERS_DIR):
        return []
    return [f for f in os.listdir(BANNERS_DIR) if os.path.isfile(os.path.join(BANNERS_DIR, f))]

BANNER_FILES = get_banner_list()

# --- Print a confirmation that the config is loaded ---
print("Configuration loaded successfully.")
if TELEGRAM_BOT_TOKEN.endswith("..."): # Basic check to avoid printing the full token
    print(f"Bot token loaded (ends with '...').")
else:
    print(f"Bot token loaded (ends with '...{TELEGRAM_BOT_TOKEN[-4:]}').")
print(f"Admin IDs: {ADMIN_IDS}")
print(f"Database path: {DATABASE_PATH}")
print(f"Banners path: {BANNERS_DIR}")