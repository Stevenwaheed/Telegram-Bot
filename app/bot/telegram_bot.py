from datetime import datetime
import os
from venv import logger
import pandas as pd
from app.config.config import Config
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, ContextTypes


class TelegramBot:
    def __init__(self):
        self.NAME, self.PHONE, self.ITEM, self.SIZE, self.COLOR, self.QUANTITY, self.ADDRESS, self.CONFIRM = range(8)
        self.EXCEL_FILE = Config.EXCEL_FILE
        
        # Pre-defined product options
        self.available_items = ["T-Shirt", "Jeans", "Dress", "Jacket", "Skirt", "Sweater"]
        self.available_colors = ["Black", "White", "Red", "Blue", "Green", "Yellow", "Pink", "Purple", "Brown", "Gray"]
        
    async def greet(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle casual greetings and start the order process."""
        await update.message.reply_text(
            f"Hello there! 👋\n\n"
            f"Welcome to our Fashion Store Bot! I'm here to help you place an order easily.\n\n"
            f"Would you like to place an order now?",
            reply_markup=ReplyKeyboardMarkup([['Start Shopping 🛍️']], one_time_keyboard=True)
        )
        return self.NAME
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the conversation and ask for the customer's name."""
        await update.message.reply_text(
            "Welcome to Fashion Bot! 🎉\n\n"
            "I'll help you place your order quickly and easily.\n\n"
            "To get started, please tell me your full name."
        )
        
        # Initialize user data dictionary
        context.user_data['order'] = {}
        
        return self.NAME

    async def name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store the name and ask for phone number."""
        user_text = update.message.text
        
        # Check if the message is "Start Shopping" button
        if user_text == "Start Shopping 🛍️":
            await update.message.reply_text(
                "Great! To get started, please tell me your full name."
            )
            # Initialize user data dictionary if not already done
            if 'order' not in context.user_data:
                context.user_data['order'] = {}
            return self.NAME
        
        # Process the name
        user_name = user_text
        context.user_data['order']['name'] = user_name
        
        await update.message.reply_text(
            f"Nice to meet you, {user_name}! 😊\n\n"
            f"Please share your phone number for order updates."
        )
        
        return self.PHONE

    async def phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store the phone number and ask what they want to order."""
        phone_number = update.message.text
        context.user_data['order']['phone'] = phone_number
        
        # Create a keyboard with available items
        item_keyboard = []
        row = []
        for i, item in enumerate(self.available_items):
            row.append(item)
            # Create a new row after every 2 items
            if (i + 1) % 2 == 0 or i == len(self.available_items) - 1:
                item_keyboard.append(row)
                row = []
        
        # Add "Other" option as the last row
        item_keyboard.append(["Other"])
        
        await update.message.reply_text(
            "What would you like to order from our collection?",
            reply_markup=ReplyKeyboardMarkup(item_keyboard, one_time_keyboard=True)
        )
        
        return self.ITEM

    async def item(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store the item and ask for size."""
        item_name = update.message.text
        context.user_data['order']['item'] = item_name
        
        size_keyboard = [['XS', 'S', 'M'], ['L', 'XL', 'XXL'], ['Other']]
        
        await update.message.reply_text(
            f"Great choice! You selected: {item_name} ✨\n\n"
            f"What size would you like?",
            reply_markup=ReplyKeyboardMarkup(size_keyboard, one_time_keyboard=True)
        )
        
        return self.SIZE

    async def size(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store the size and ask for color."""
        size_choice = update.message.text
        context.user_data['order']['size'] = size_choice
        
        # Create a keyboard with available colors
        color_keyboard = []
        row = []
        for i, color in enumerate(self.available_colors):
            row.append(color)
            # Create a new row after every 3 colors
            if (i + 1) % 3 == 0 or i == len(self.available_colors) - 1:
                color_keyboard.append(row)
                row = []
        
        # Add "Other" option as the last row
        color_keyboard.append(["Other"])
        
        await update.message.reply_text(
            f"Selected size: {size_choice}\n\n"
            f"What color would you prefer?",
            reply_markup=ReplyKeyboardMarkup(color_keyboard, one_time_keyboard=True)
        )
        
        return self.COLOR

    async def color(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store the color and ask for quantity."""
        color_choice = update.message.text
        context.user_data['order']['color'] = color_choice
        
        quantity_keyboard = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9'], ['Other']]
        
        await update.message.reply_text(
            f"Selected color: {color_choice} 🎨\n\n"
            f"How many would you like to order?",
            reply_markup=ReplyKeyboardMarkup(quantity_keyboard, one_time_keyboard=True)
        )
        
        return self.QUANTITY

    async def quantity(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store the quantity and ask for address."""
        quantity_choice = update.message.text
        context.user_data['order']['quantity'] = quantity_choice
        
        await update.message.reply_text(
            f"Quantity: {quantity_choice}\n\n"
            f"Please provide your complete delivery address.",
            reply_markup=ReplyKeyboardRemove()
        )
        
        return self.ADDRESS

    async def address(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store the address and ask for confirmation."""
        address_text = update.message.text
        context.user_data['order']['address'] = address_text
        
        order = context.user_data['order']
        
        # Calculate total price (mock calculation - you can modify this)
        try:
            quantity = int(order['quantity'])
            # Mock base price - you would replace this with your actual pricing
            base_price = 29.99
            total_price = base_price * quantity
        except:
            total_price = 0
        
        # Show order summary
        await update.message.reply_text(
            f"📋 ORDER SUMMARY:\n\n"
            f"Name: {order['name']}\n"
            f"Phone: {order['phone']}\n"
            f"Item: {order['item']}\n"
            f"Size: {order['size']}\n"
            f"Color: {order['color']}\n"
            f"Quantity: {order['quantity']}\n"
            f"Delivery address: {order['address']}\n"
            f"Estimated total: ${total_price:.2f}\n\n"
            f"Is this correct?",
            reply_markup=ReplyKeyboardMarkup([['✅ Confirm Order', '❌ Cancel Order']], one_time_keyboard=True)
        )
        
        return self.CONFIRM

    async def confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Save order to Excel and end conversation."""
        response = update.message.text
        
        if response == "✅ Confirm Order":
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
            
            # Send notification to shop owner
            try:
                # Format the order details for the shop owner
                owner_notification = (
                    f"🔔 NEW ORDER ALERT! 🔔\n\n"
                    f"Order ID: {order_id}\n"
                    f"Date/Time: {order_data['timestamp']}\n\n"
                    f"Customer: {order_data['customer_name']}\n"
                    f"Phone: {order_data['phone_number']}\n\n"
                    f"Item: {order_data['item']}\n"
                    f"Size: {order_data['size']}\n"
                    f"Color: {order_data['color']}\n"
                    f"Quantity: {order_data['quantity']}\n\n"
                    f"Delivery to: {order_data['address']}\n\n"
                    f"Please process this order soon!"
                )
                
                # Send notification to the shop owner's Telegram ID
                await context.bot.send_message(
                    chat_id=Config.SHOP_OWNER_TELEGRAM_ID,  # You need to add this to your Config
                    text=owner_notification
                )
                logger.info(f"Owner notification sent for order {order_id}")
            except Exception as e:
                logger.error(f"Failed to send owner notification: {e}")
                
            # Confirm order to customer
            await update.message.reply_text(
                f"🎉 Thank you! Your order has been placed successfully.\n\n"
                f"Your order ID is: {order_id}\n\n"
                f"We will process your order soon and contact you for delivery details.\n"
                f"If you have any questions, please mention your order ID.\n\n"
                f"To place another order, just say 'hi' or use the /start command.",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await update.message.reply_text(
                "Order cancelled. Feel free to start a new order anytime by saying 'hi' or using the /start command.",
                reply_markup=ReplyKeyboardRemove()
            )
        
        # Clear user data
        context.user_data.clear()
        return ConversationHandler.END


    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel and end the conversation."""
        await update.message.reply_text(
            "Order cancelled. Feel free to start a new order anytime by saying 'hi' or using the /start command.",
            reply_markup=ReplyKeyboardRemove()
        )
        
        # Clear user data
        context.user_data.clear()
        return ConversationHandler.END