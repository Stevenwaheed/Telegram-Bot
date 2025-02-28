from datetime import datetime
import os
import pandas as pd
from app.config.config import Config
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, ContextTypes


class TelegramBot:
    def __init__(self):
        self.NAME, self.PHONE, self.ITEM, self.SIZE, self.COLOR, self.QUANTITY, self.ADDRESS, self.CONFIRM = range(8)
        self.EXCEL_FILE = Config.EXCEL_FILE
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the conversation and ask for the customer's name."""
        await update.message.reply_text(
            "Welcome to Fashion Bot! I'll help you place your order. "
            "Please tell me your full name."
        )
        
        # Initialize user data dictionary
        context.user_data['order'] = {}
        
        return self.NAME

    async def name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store the name and ask for phone number."""
        user_name = update.message.text
        context.user_data['order']['name'] = user_name
        
        await update.message.reply_text(
            f"Nice to meet you, {user_name}! Please share your phone number for order updates."
        )
        
        return self.PHONE

    async def phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store the phone number and ask what they want to order."""
        phone_number = update.message.text
        context.user_data['order']['phone'] = phone_number
        
        await update.message.reply_text(
            "What item would you like to order from our collection?"
        )
        
        return self.ITEM

    async def item(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store the item and ask for size."""
        item_name = update.message.text
        context.user_data['order']['item'] = item_name
        
        size_keyboard = [['XS', 'S', 'M'], ['L', 'XL', 'XXL'], ['Other']]
        
        await update.message.reply_text(
            "What size would you like?",
            reply_markup=ReplyKeyboardMarkup(size_keyboard, one_time_keyboard=True)
        )
        
        return self.SIZE

    async def size(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store the size and ask for color."""
        size_choice = update.message.text
        context.user_data['order']['size'] = size_choice
        
        await update.message.reply_text(
            "What color would you prefer?",
            reply_markup=ReplyKeyboardRemove()
        )
        
        return self.COLOR

    async def color(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store the color and ask for quantity."""
        color_choice = update.message.text
        context.user_data['order']['color'] = color_choice
        
        quantity_keyboard = [['1', '2', '3'], ['4', '5', 'Other']]
        
        await update.message.reply_text(
            "How many would you like to order?",
            reply_markup=ReplyKeyboardMarkup(quantity_keyboard, one_time_keyboard=True)
        )
        
        return self.QUANTITY

    async def quantity(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store the quantity and ask for address."""
        quantity_choice = update.message.text
        context.user_data['order']['quantity'] = quantity_choice
        
        await update.message.reply_text(
            "Please provide your complete delivery address.",
            reply_markup=ReplyKeyboardRemove()
        )
        
        return self.ADDRESS

    async def address(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store the address and ask for confirmation."""
        address_text = update.message.text
        context.user_data['order']['address'] = address_text
        
        order = context.user_data['order']
        
        # Show order summary
        await update.message.reply_text(
            f"Please confirm your order details:\n\n"
            f"Name: {order['name']}\n"
            f"Phone: {order['phone']}\n"
            f"Item: {order['item']}\n"
            f"Size: {order['size']}\n"
            f"Color: {order['color']}\n"
            f"Quantity: {order['quantity']}\n"
            f"Delivery address: {order['address']}\n\n"
            f"Is this correct? (Yes/No)",
            reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True)
        )
        
        return self.CONFIRM

    async def confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Save order to Excel and end conversation."""
        response = update.message.text.lower()
        
        if response == 'yes':
            # Generate order ID
            order_id = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Prepare data for Excel
            order_data = {
                'order_id': order_id,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'customer_name': context.user_data['order']['name'],
                'phone_number': context.user_data['order']['phone'],
                'item': context.user_data['order']['item'],
                'size': context.user_data['order']['size'],
                'color': context.user_data['order']['color'],
                'quantity': context.user_data['order']['quantity'],
                'address': context.user_data['order']['address'],
                'status': 'New'
            }
            
            # Load existing Excel file
            if os.path.exists(Config.EXCEL_FILE):
                df = pd.read_excel(Config.EXCEL_FILE)
            else:
                # Create new DataFrame if file doesn't exist
                df = pd.DataFrame(columns=[
                    'order_id', 'timestamp', 'customer_name', 'phone_number', 
                    'item', 'size', 'color', 'quantity', 'address', 'status'
                ])
            
            # Append new order
            df = pd.concat([df, pd.DataFrame([order_data])], ignore_index=True)
            
            # Save to Excel
            df.to_excel(Config.EXCEL_FILE, index=False)
            
            await update.message.reply_text(
                f"Thank you! Your order has been placed successfully. "
                f"Your order ID is: {order_id}\n\n"
                f"We will process your order soon. "
                f"If you have any questions, please mention your order ID.",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await update.message.reply_text(
                "No problem! Let's try again. Please use the /start command to place a new order.",
                reply_markup=ReplyKeyboardRemove()
            )
        
        # Clear user data
        context.user_data.clear()
        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel and end the conversation."""
        await update.message.reply_text(
            "Order cancelled. Feel free to start a new order anytime with /start",
            reply_markup=ReplyKeyboardRemove()
        )
        
        # Clear user data
        context.user_data.clear()
        return ConversationHandler.END