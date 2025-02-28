import os
from dotenv import load_dotenv

class Config:
    load_dotenv(dotenv_path=".env", override=True)
    YOUR_TELEGRAM_BOT_TOKEN = os.getenv('YOUR_TELEGRAM_BOT_TOKEN')
    EXCEL_FILE = os.getenv('EXCEL_FILE')