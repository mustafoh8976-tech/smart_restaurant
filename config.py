import os
from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_NAME = os.getenv('DB_NAME', 'restaurant')
DB_PASSWORD = os.getenv('DB_PASSWORD')

ADMIN_IDS = [int(user_id.strip()) for user_id in os.getenv('ADMIN_IDS', '').split(',') if user_id.strip()]
STAFF_IDS = [int(user_id.strip()) for user_id in os.getenv('STAFF_IDS', '').split(',') if user_id.strip()]
