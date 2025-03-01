from datetime import datetime
import os
from venv import logger
import pandas as pd
from app.config.config import Config
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, ContextTypes


class TelegramBot:
    def __init__(self):
        # Add language selection state
        self.LANGUAGE, self.NAME, self.PHONE, self.ITEM, self.SIZE, self.COLOR, self.QUANTITY, self.ADDRESS, self.CONFIRM = range(9)
        self.EXCEL_FILE = Config.EXCEL_FILE
        
        # Pre-defined product options
        self.available_items = {
            "en": ["T-Shirt", "Jeans", "Dress", "Jacket", "Skirt", "Sweater"],
            "id": ["Kaos", "Celana Jeans", "Gaun", "Jaket", "Rok", "Sweater"]
        }
        self.available_colors = {
            "en": ["Black", "White", "Red", "Blue", "Green", "Yellow", "Pink", "Purple", "Brown", "Gray"],
            "id": ["Hitam", "Putih", "Merah", "Biru", "Hijau", "Kuning", "Merah Muda", "Ungu", "Coklat", "Abu-abu"]
        }
        
        # Text translations
        self.translations = {
            "en": {
                "welcome": "Hello there! 👋\n\nWelcome to Fee Fashion Store Bot! I'm here to help you place an order easily.\n\nWould you like to place an order now?",
                "start_shopping": "Start Shopping 🛍️",
                "language_selection": "Please select your preferred language:",
                "english": "English 🇬🇧",
                "indonesian": "Bahasa Indonesia 🇮🇩",
                "start_message": "Welcome to Fashion Bot! 🎉\n\nI'll help you place your order quickly and easily.\n\nTo get started, please tell me your full name.",
                "ask_name": "Great! To get started, please tell me your full name.",
                "nice_meet": "Nice to meet you, {}! 😊\n\nPlease share your phone number for order updates.",
                "invalid_phone": "⚠️ That doesn't look like a valid phone number.\n\nPlease provide a valid phone number with at least 10 digits.\nFor example: 1234567890 or +1 (123) 456-7890",
                "phone_too_long": "⚠️ The phone number you entered has too many digits.\n\nPlease provide a valid phone number.\nFor example: 1234567890 or +1 (123) 456-7890",
                "phone_invalid_chars": "⚠️ Please enter a valid phone number containing only digits, optionally with a + prefix for country code.\n\nFor example: 1234567890 or +1 (123) 456-7890",
                "phone_verified": "Great! Your phone number has been verified ✅\n\nWhat would you like to order from our collection?",
                "great_choice": "Great choice! You selected: {} ✨\n\nWhat size would you like?",
                "selected_size": "Selected size: {}\n\nWhat color would you prefer?",
                "selected_color": "Selected color: {} 🎨\n\nHow many would you like to order?",
                "quantity_selected": "Quantity: {}\n\nPlease provide your complete delivery address.",
                "order_summary": "📋 ORDER SUMMARY:\n\nName: {}\nPhone: {}\nItem: {}\nSize: {}\nColor: {}\nQuantity: {}\nDelivery address: {}\nEstimated total: ${:.2f}\n\nIs this correct?",
                "confirm_order": "✅ Confirm Order",
                "cancel_order": "❌ Cancel Order",
                "order_success": "🎉 Thank you! Your order has been placed successfully.\n\nYour order ID is: {}\n\nWe will process your order soon and contact you for delivery details.\nIf you have any questions, please mention your order ID.\n\nTo place another order, just say 'hi' or use the /start command.",
                "order_cancelled": "Order cancelled. Feel free to start a new order anytime by saying 'hi' or using the /start command.",
                "other": "Other"
            },
            "id": {
                "welcome": "Halo! 👋\n\nSelamat datang di Bot Toko Fashion Fee! Saya siap membantu Anda melakukan pemesanan dengan mudah.\n\nApakah Anda ingin memesan sekarang?",
                "start_shopping": "Mulai Berbelanja 🛍️",
                "language_selection": "Silakan pilih bahasa yang Anda inginkan:",
                "english": "English 🇬🇧",
                "indonesian": "Bahasa Indonesia 🇮🇩",
                "start_message": "Selamat datang di Bot Fashion! 🎉\n\nSaya akan membantu Anda memesan dengan cepat dan mudah.\n\nUntuk memulai, mohon beritahu nama lengkap Anda.",
                "ask_name": "Bagus! Untuk memulai, mohon beritahu nama lengkap Anda.",
                "nice_meet": "Senang bertemu dengan Anda, {}! 😊\n\nMohon bagikan nomor telepon Anda untuk pembaruan pesanan.",
                "invalid_phone": "⚠️ Sepertinya nomor telepon tidak valid.\n\nMohon berikan nomor telepon valid dengan minimal 10 digit.\nContoh: 1234567890 atau +62 812 3456 7890",
                "phone_too_long": "⚠️ Nomor telepon yang Anda masukkan terlalu banyak digit.\n\nMohon berikan nomor telepon yang valid.\nContoh: 1234567890 atau +62 812 3456 7890",
                "phone_invalid_chars": "⚠️ Mohon masukkan nomor telepon valid yang hanya berisi angka, dengan awalan + opsional untuk kode negara.\n\nContoh: 1234567890 atau +62 812 3456 7890",
                "phone_verified": "Bagus! Nomor telepon Anda telah diverifikasi ✅\n\nApa yang ingin Anda pesan dari koleksi kami?",
                "great_choice": "Pilihan bagus! Anda memilih: {} ✨\n\nUkuran apa yang Anda inginkan?",
                "selected_size": "Ukuran yang dipilih: {}\n\nWarna apa yang Anda sukai?",
                "selected_color": "Warna yang dipilih: {} 🎨\n\nBerapa banyak yang ingin Anda pesan?",
                "quantity_selected": "Jumlah: {}\n\nMohon berikan alamat pengiriman lengkap Anda.",
                "order_summary": "📋 RINGKASAN PESANAN:\n\nNama: {}\nTelepon: {}\nBarang: {}\nUkuran: {}\nWarna: {}\nJumlah: {}\nAlamat pengiriman: {}\nTotal estimasi: Rp{:.2f}\n\nApakah ini benar?",
                "confirm_order": "✅ Konfirmasi Pesanan",
                "cancel_order": "❌ Batalkan Pesanan",
                "order_success": "🎉 Terima kasih! Pesanan Anda telah berhasil dibuat.\n\nID pesanan Anda adalah: {}\n\nKami akan segera memproses pesanan Anda dan menghubungi Anda untuk detail pengiriman.\nJika Anda memiliki pertanyaan, harap sebutkan ID pesanan Anda.\n\nUntuk membuat pesanan lain, cukup katakan 'hai' atau gunakan perintah /start.",
                "order_cancelled": "Pesanan dibatalkan. Jangan ragu untuk memulai pesanan baru kapan saja dengan mengatakan 'hai' atau menggunakan perintah /start.",
                "other": "Lainnya"
            }
        }
        
    async def greet(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle casual greetings and prompt for language selection."""
        # Initialize user data dictionary if it doesn't exist
        if 'order' not in context.user_data:
            context.user_data['order'] = {}
            
        # Initialize language to default
        context.user_data['language'] = 'en'  # Default to English
        
        # Offer language selection
        await update.message.reply_text(
            "Please select your preferred language / Silakan pilih bahasa yang Anda inginkan:",
            reply_markup=ReplyKeyboardMarkup([
                ["English 🇬🇧", "Bahasa Indonesia 🇮🇩"]
            ], one_time_keyboard=True)
        )
        
        return self.LANGUAGE
    
    async def select_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle language selection and continue to welcome message."""
        user_choice = update.message.text
        
        # Set language based on user selection
        if "Bahasa Indonesia" in user_choice:
            context.user_data['language'] = 'id'
        else:
            context.user_data['language'] = 'en'
            
        lang = context.user_data['language']
        
        # Now show the welcome message in the selected language
        await update.message.reply_text(
            self.translations[lang]["welcome"],
            reply_markup=ReplyKeyboardMarkup([[self.translations[lang]["start_shopping"]]], one_time_keyboard=True)
        )
        
        return self.NAME
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the conversation and prompt for language selection."""
        # Initialize user data dictionary
        context.user_data['order'] = {}
        
        # Initialize language to default
        context.user_data['language'] = 'en'  # Default to English
        
        # Offer language selection
        await update.message.reply_text(
            "Please select your preferred language / Silakan pilih bahasa yang Anda inginkan:",
            reply_markup=ReplyKeyboardMarkup([
                ["English 🇬🇧", "Bahasa Indonesia 🇮🇩"]
            ], one_time_keyboard=True)
        )
        
        return self.LANGUAGE

    async def name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store the name and ask for phone number."""
        # Get language from user data
        lang = context.user_data.get('language', 'en')
        user_text = update.message.text
        
        # Check if the message is "Start Shopping" button
        if user_text == self.translations[lang]["start_shopping"]:
            await update.message.reply_text(
                self.translations[lang]["ask_name"]
            )
            return self.NAME
        
        # Process the name
        user_name = user_text
        context.user_data['order']['name'] = user_name
        
        await update.message.reply_text(
            self.translations[lang]["nice_meet"].format(user_name)
        )
        
        return self.PHONE

    async def phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Validate and store the phone number, then ask what they want to order."""
        lang = context.user_data.get('language', 'en')
        phone_number = update.message.text
        
        # Initial check if input contains enough digits
        digit_count = sum(1 for char in phone_number if char.isdigit())
        
        # Validate if the input actually has numeric content
        if digit_count < 10:
            await update.message.reply_text(
                self.translations[lang]["invalid_phone"]
            )
            return self.PHONE
        
        # Remove any non-digit characters except the leading + for country code
        if phone_number.startswith('+'):
            cleaned_number = '+' + ''.join(char for char in phone_number[1:] if char.isdigit())
        else:
            cleaned_number = ''.join(char for char in phone_number if char.isdigit())
        
        # Additional check for maximum reasonable length
        if len(cleaned_number.replace('+', '')) > 15:
            await update.message.reply_text(
                self.translations[lang]["phone_too_long"]
            )
            return self.PHONE
        
        # Check if all digits after potential + sign
        if not cleaned_number.replace('+', '').isdigit():
            await update.message.reply_text(
                self.translations[lang]["phone_invalid_chars"]
            )
            return self.PHONE
        
        # Store the validated phone number
        context.user_data['order']['phone'] = cleaned_number
        
        # Create a keyboard with available items in the correct language
        item_keyboard = []
        row = []
        for i, item in enumerate(self.available_items[lang]):
            row.append(item)
            # Create a new row after every 2 items
            if (i + 1) % 2 == 0 or i == len(self.available_items[lang]) - 1:
                item_keyboard.append(row)
                row = []
        
        # Add "Other" option as the last row
        item_keyboard.append([self.translations[lang]["other"]])
        
        await update.message.reply_text(
            self.translations[lang]["phone_verified"],
            reply_markup=ReplyKeyboardMarkup(item_keyboard, one_time_keyboard=True)
        )
        
        return self.ITEM

    async def item(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store the item and ask for size."""
        lang = context.user_data.get('language', 'en')
        item_name = update.message.text
        context.user_data['order']['item'] = item_name
        
        size_keyboard = [['XS', 'S', 'M'], ['L', 'XL', 'XXL'], [self.translations[lang]["other"]]]
        
        await update.message.reply_text(
            self.translations[lang]["great_choice"].format(item_name),
            reply_markup=ReplyKeyboardMarkup(size_keyboard, one_time_keyboard=True)
        )
        
        return self.SIZE

    async def size(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store the size and ask for color."""
        lang = context.user_data.get('language', 'en')
        size_choice = update.message.text
        context.user_data['order']['size'] = size_choice
        
        # Create a keyboard with available colors in correct language
        color_keyboard = []
        row = []
        for i, color in enumerate(self.available_colors[lang]):
            row.append(color)
            # Create a new row after every 3 colors
            if (i + 1) % 3 == 0 or i == len(self.available_colors[lang]) - 1:
                color_keyboard.append(row)
                row = []
        
        # Add "Other" option as the last row
        color_keyboard.append([self.translations[lang]["other"]])
        
        await update.message.reply_text(
            self.translations[lang]["selected_size"].format(size_choice),
            reply_markup=ReplyKeyboardMarkup(color_keyboard, one_time_keyboard=True)
        )
        
        return self.COLOR

    async def color(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store the color and ask for quantity."""
        lang = context.user_data.get('language', 'en')
        color_choice = update.message.text
        context.user_data['order']['color'] = color_choice
        
        quantity_keyboard = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9'], [self.translations[lang]["other"]]]
        
        await update.message.reply_text(
            self.translations[lang]["selected_color"].format(color_choice),
            reply_markup=ReplyKeyboardMarkup(quantity_keyboard, one_time_keyboard=True)
        )
        
        return self.QUANTITY

    async def quantity(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store the quantity and ask for address."""
        lang = context.user_data.get('language', 'en')
        quantity_choice = update.message.text
        context.user_data['order']['quantity'] = quantity_choice
        
        await update.message.reply_text(
            self.translations[lang]["quantity_selected"].format(quantity_choice),
            reply_markup=ReplyKeyboardRemove()
        )
        
        return self.ADDRESS

    async def address(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store the address and ask for confirmation."""
        lang = context.user_data.get('language', 'en')
        address_text = update.message.text
        context.user_data['order']['address'] = address_text
        
        order = context.user_data['order']
        
        # Calculate total price (mock calculation - you can modify this)
        try:
            quantity = int(order['quantity'])
            # Mock base price - you would replace this with your actual pricing
            base_price = 29.99
            # For Indonesian language, convert to Rupiah (approx 1 USD = 14,500 IDR)
            if lang == 'id':
                base_price = base_price * 14500
            total_price = base_price * quantity
        except:
            total_price = 0
        
        # Show order summary
        await update.message.reply_text(
            self.translations[lang]["order_summary"].format(
                order['name'],
                order['phone'],
                order['item'],
                order['size'],
                order['color'],
                order['quantity'],
                order['address'],
                total_price
            ),
            reply_markup=ReplyKeyboardMarkup([
                [self.translations[lang]["confirm_order"], self.translations[lang]["cancel_order"]]
            ], one_time_keyboard=True)
        )
        
        return self.CONFIRM

    async def confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Save order to Excel and end conversation."""
        lang = context.user_data.get('language', 'en')
        response = update.message.text
        
        if response == self.translations[lang]["confirm_order"]:
            # Generate order ID
            order_id = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Prepare data for Excel
            order_data = {
                'order_id': order_id,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'language': lang,
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
                    'order_id', 'timestamp', 'language', 'customer_name', 'phone_number',
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
                    f"Date/Time: {order_data['timestamp']}\n"
                    f"Language: {lang.upper()}\n\n"
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
                self.translations[lang]["order_success"].format(order_id),
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await update.message.reply_text(
                self.translations[lang]["order_cancelled"],
                reply_markup=ReplyKeyboardRemove()
            )
        
        # Clear user data
        context.user_data.clear()
        return ConversationHandler.END


    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel and end the conversation."""
        lang = context.user_data.get('language', 'en')  # Default to English if not set
        await update.message.reply_text(
            self.translations[lang]["order_cancelled"],
            reply_markup=ReplyKeyboardRemove()
        )
        
        # Clear user data
        context.user_data.clear()
        return ConversationHandler.END