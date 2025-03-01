import logging
from app.config.config import Config
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
import pandas as pd
import os
from app.bot.telegram_bot import TelegramBot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create Excel file if it doesn't exist
def initialize_excel():
    if not os.path.exists(Config.EXCEL_FILE):
        df = pd.DataFrame(columns=[
            'order_id', 'timestamp', 'customer_name', 'phone_number',
            'item', 'size', 'color', 'quantity', 'address', 'status'
        ])
        df.to_excel(Config.EXCEL_FILE, index=False)
        print(f"Created new Excel file: {Config.EXCEL_FILE}")

def main() -> None:
    """Run the bot."""
    # Initialize Excel file
    initialize_excel()
    
    telegram_bot = TelegramBot()
    
    # Create the Application
    application = Application.builder().token(Config.YOUR_TELEGRAM_BOT_TOKEN).build()
    
    # Add conversation handler with states
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", telegram_bot.start),
            # Add message handler to catch 'hi' and other greetings
            MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_bot.greet)
        ],
        states={
            telegram_bot.LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_bot.select_language)],
            telegram_bot.NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_bot.name)],
            telegram_bot.PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_bot.phone)],
            telegram_bot.ITEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_bot.item)],
            telegram_bot.SIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_bot.size)],
            telegram_bot.COLOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_bot.color)],
            telegram_bot.QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_bot.quantity)],
            telegram_bot.ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_bot.address)],
            telegram_bot.CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_bot.confirm)],
        },
        fallbacks=[CommandHandler("cancel", telegram_bot.cancel)],
    )
    
    application.add_handler(conv_handler)
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()