import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def format_message(message: str) -> str:
    return message.strip()

def log_user_activity(user_id: int, activity: str):
    logging.info(f"User {user_id}: {activity}")