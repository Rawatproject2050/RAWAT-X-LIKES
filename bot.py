import telebot
from telebot import types
import sqlite3
import os
import threading
from flask import Flask

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Database Setup
def init_db():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            plan_name TEXT,
            utr_number TEXT,
            game_uid TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

user_states = {}

def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🚀 Start Bot"),
        types.KeyboardButton("💎 Buy Likes & Pricing"),
        types.KeyboardButton("ℹ️ Help & Trust Guide"),
        types.KeyboardButton("👑 Admin Dashboard")
    )
    return markup

# /start & Main Menu Handler
@bot.message_handler(commands=['start'])
@bot.message_handler(func=lambda message: message.text in ["🚀 Start Bot", "💎 Buy Likes & Pricing"])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Pricing Buttons (Professional layout)
    markup.add(
        types.InlineKeyboardButton("🟢 ₹5 — 40 Likes", callback_data='plan_5'),
        types.InlineKeyboardButton("🟡 ₹10 — 90 Likes", callback_data='plan_10'),
        types.InlineKeyboardButton("🟡 ₹15 — 145 Likes", callback_data='plan_15'),
        types.InlineKeyboardButton("🔵 ₹20 — 205 Likes", callback_data='plan_20'),
        types.InlineKeyboardButton("🔵 ₹25 — 270 Likes", callback_data='plan_25'),
        types.InlineKeyboardButton("🟣 ₹30 — 340 Likes", callback_data='plan_30'),
        types.InlineKeyboardButton("🟣 ₹35 — 415 Likes", callback_data='plan_35'),
        types.InlineKeyboardButton("🔥 ₹40 — 500 Likes", callback_data='plan_40'),
        types.InlineKeyboardButton("🔥 ₹45 — 585 Likes", callback_data='plan_45'),
        types.InlineKeyboardButton("🚀 ₹50 — 700 Likes (Best)", callback_data='plan_50')
    )

    text = (
        "🔥 **FREE FIRE DAILY LIKES SERVICE** 🔥\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ *Get fast, secure and genuine profile likes everyday.*\n\n"
        "💎 **CHOOSE YOUR PLAN BELOW:**\n"
        "*(Bade plans par zyada likes aur bada fayda milta hai!)*\n\n"
        "🛡️ **Safety Guarantee:** Garena rules ke mutabiq daily limit mein likes diye jaate hain taaki ID 100% safe rahe."
    )
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=get_main_menu())
    bot.send_message(message.chat.id, "👇 *Apna pasandida plan select karne ke liye button dabayein:*", parse_mode='Markdown', reply_markup=markup)

# Help & Trust Guide
@bot.message_handler(func=lambda message: message.text == "ℹ️ Help & Trust Guide")
def help_info(message):
    text = (
        "🛡️ **TRUST & SAFETY GUIDE**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "• **Garena Rules Safe:** Hum limit ke sath likes bhejte hain, bachi hui likes agle din milti hain.\n"
        "• **Zero Ban Risk:** Aapki ID par koi khatra nahi hota.\n"
        "• **Fast Support:** Payment ke baad turant UTR aur UID submit karein."
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=get_main_menu())

# Admin Dashboard
@bot.message_handler(func=lambda message: message.text == "👑 Admin Dashboard")
def admin_dashboard(message):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders")
    count = cursor.fetchone()[0]
    conn.close()

    text = (
        "👑 **ADMIN CONTROL PANEL**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 Total Orders: `{count}`\n\n"
        "💻 *Command:* Type `/list` to view customer records."
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=get_main_menu())

# Plan Selected -> Show Professional Card with Payment Options (QR / UPI)
@bot.callback_query_handler(func=lambda call: call.data.startswith('plan_'))
def handle_plan_selection(call):
    prices = {
        'plan_5': ("₹5", "40 Likes"), 'plan_10': ("₹10", "90 Likes"),
        'plan_15': ("₹15", "145 Likes"), 'plan_20': ("₹20", "205 Likes"),
        'plan_25': ("₹25", "270 Likes"), 'plan_30': ("₹30", "340 Likes"),
        'plan_35': ("₹35", "415 Likes"), 'plan_40': ("₹40", "500 Likes"),
        'plan_45': ("₹45", "585 Likes"), 'plan_50': ("₹50", "700 Likes")
    }
    
    price, likes = prices.get(call.data, ("₹5", "40 Likes"))
    user_states[call.from_user.id] = {'state': 'waiting_for_utr', 'plan': f"{price} - {likes}"}
    bot.answer_callback_query(call.id)

    # Card-style professional layout
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📷 View QR Code", callback_data='show_qr'),
        types.InlineKeyboardButton("📋 Copy UPI ID", callback_data='show_upi')
    )
    markup.add(types.InlineKeyboardButton("✅ Payment Ho Gaya (Send UTR)", callback_data='send_utr_prompt'))

    card_text = (
        f"📦 **ORDER SUMMARY CARD**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔹 **Plan:** `{price} — {likes}`\n"
        f"👤 **Name:** Santosh Rawat\n\n"
        f"⚠️ **Trust Notice:** Garena rules ke tahat daily limit me likes milenge taaki ID 100% safe rahe.\n\n"
        f"👇 **Payment karne ke liye niche option chunein:**"
    )
    
    bot.send_message(call.message.chat.id, card_text, parse_mode='Markdown', reply_markup=markup)

# Handle QR Code Button Click (Sends direct image from your link)
@bot.callback_query_handler(func=lambda call: call.data == 'show_qr')
def send_qr_image(call):
    bot.answer_callback_query(call.id)
    qr_url = "https://i.postimg.cc/kGQwSRy4/QR-Code.png"
    
    caption = (
        "📷 **SCAN & PAY VIA QR**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "• Is QR code ko apne kisi bhi UPI app (GPay/PhonePe/Paytm) se scan karke exact amount pay karein.\n"
        "• Payment ke baad niche button daba kar UTR bhejein."
    )
    bot.send_photo(call.message.chat.id, qr_url, caption=caption, parse_mode='Markdown')

# Handle UPI ID Button Click (Clean card view)
@bot.callback_query_handler(func=lambda call: call.data == 'show_upi')
def send_upi_details(call):
    bot.answer_callback_query(call.id)
    
    upi_text = (
        "💳 **DIRECT UPI PAYMENT**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Aap niche di gayi UPI ID par seedha payment kar sakte hain:\n\n"
        "🆔 `santoshkumarram085-1@oksbi`\n"
        "👤 **Name:** Santosh Rawat\n\n"
        "*(Tap to copy above UPI ID)*"
    )
    bot.send_message(call.message.chat.id, upi_text, parse_mode='Markdown')

# Prompt user for UTR when they click "Payment Ho Gaya"
@bot.callback_query_handler(func=lambda call: call.data == 'send_utr_prompt')
def prompt_utr(call):
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        "📝 **ENTER TRANSACTION DETAILS**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Kripya apne payment ka **12-digit UTR / Reference Number** yahan chat mein type karke bhejein:",
        parse_mode='Markdown'
    )

# Handle text inputs (UTR & Game UID sequence)
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    state = user_states.get(user_id)

    if isinstance(state, dict) and state.get('state') == 'waiting_for_utr':
        utr = message.text.strip()
        plan_selected = state.get('plan')
        user_states[user_id] = {'state': 'waiting_for_uid', 'utr': utr, 'plan': plan_selected}

        bot.reply_to(
            message,
            "✅ **UTR RECEIVED SUCCESSFULLY!**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📦 Plan: `{plan_selected}`\n"
            f"🔢 UTR: `{utr}`\n\n"
            "🎯 **Aakhri Step:** Ab aap apna **Free Fire Game UID** yahan bhejein jahan likes bhejne hain:",
            parse_mode='Markdown'
        )

    elif isinstance(state, dict) and state.get('state') == 'waiting_for_uid':
        game_uid = message.text.strip()
        utr = state.get('utr')
        plan_selected = state.get('plan')
        username = message.from_user.username or message.from_user.first_name

        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (user_id, username, plan_name, utr_number, game_uid, status) VALUES (?, ?, ?, ?, ?, ?)",
                       (user_id, username, plan_selected, utr, game_uid, 'Pending'))
        conn.commit()
        conn.close()

        user_states.pop(user_id, None)

        bot.reply_to(
            message,
            "🎉 **ORDER PLACED SUCCESSFULLY!**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📦 Plan: `{plan_selected}`\n"
            f"🆔 UID: `{game_uid}`\n"
            f"🔢 UTR: `{utr}`\n\n"
            "Admin dwara payment verify hote hi aapka daily likes process shuru kar diya jayega! 🚀",
            parse_mode='Markdown',
            reply_markup=get_main_menu()
        )
    else:
        bot.reply_to(message, "Kripya menu ka use karein ya /start dabayein.", reply_markup=get_main_menu())

# Admin Orders List
@bot.message_handler(commands=['list', 'export'])
def list_orders(message):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, username, plan_name, utr_number, game_uid, status FROM orders")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        bot.reply_to(message, "📂 Abhi tak koi order database mein nahi hai.", reply_markup=get_main_menu())
        return

    response = "📋 **CUSTOMER ORDERS DATABASE:**\n━━━━━━━━━━━━━━━━━━━━━━━\n"
    for row in rows:
        response += f"🔹 **ID:** {row[0]}\n👤 **User:** @{row[2]} (`{row[1]}`)\n📦 **Plan:** {row[3]}\n🔢 **UTR:** `{row[4]}`\n🆔 **UID:** `{row[5]}`\nStatus: {row[6]}\n----------------------------------\n"

    if len(response) > 4000:
        for x in range(0, len(response), 4000):
            bot.send_message(message.chat.id, response[x:x+4000], parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, response, parse_mode='Markdown', reply_markup=get_main_menu())

# Flask Web Service Server for Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Professional Bot Web Service is Live!"

def run_flask():
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    print("Professional Bot & Web Service running...")
    bot.infinity_polling()
