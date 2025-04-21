import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Check for required environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
telegram_api_token = os.getenv("TELEGRAM_API_TOKEN")
admin_user_id = os.getenv("ADMIN_USER_ID")

if not openai_api_key:
    logging.error("OPENAI_API_KEY is not set")
    raise ValueError("OPENAI_API_KEY is not set")
if not telegram_api_token:
    logging.error("TELEGRAM_API_TOKEN is not set")
    raise ValueError("TELEGRAM_API_TOKEN is not set")
if not admin_user_id:
    logging.error("ADMIN_USER_ID is not set")
    raise ValueError("ADMIN_USER_ID is not set")

# Admin user ID
ADMIN_USER_ID = int(admin_user_id)