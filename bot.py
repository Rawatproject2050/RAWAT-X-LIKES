import telebot
from telebot import types
import sqlite3
import os
import threading
from flask import Flask

# Render Environment Variables se securely uthayega
TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '6665529050'))

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
            likes_count INTEGER,
            utr_number TEXT,
            game_uid TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

user_states = {}

def get_main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🚀 Start Bot"),
        types.KeyboardButton("💎 Buy Likes & Pricing"),
        types.KeyboardButton("ℹ️ Help & Trust Guide")
    )
    if user_id == ADMIN_ID:
        markup.add(types.KeyboardButton("👑 Admin Dashboard"))
    return markup

# Safe delete helper function to keep chat clean
def safe_delete(chat_id, message_id):
    try:
        bot.delete_message(chat_id, message_id)
    except Exception:
        pass

# /start & Main Menu Handler (Menu button hamesha niche rahega)
@bot.message_handler(commands=['start'])
@bot.message_handler(func=lambda message: message.text in ["🚀 Start Bot", "💎 Buy Likes & Pricing"])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🟢 ₹5 — 40 Likes", callback_data='plan_5_40'),
        types.InlineKeyboardButton("🟡 ₹10 — 90 Likes", callback_data='plan_10_90'),
        types.InlineKeyboardButton("🟡 ₹15 — 145 Likes", callback_data='plan_15_145'),
        types.InlineKeyboardButton("🔵 ₹20 — 205 Likes", callback_data='plan_20_205'),
        types.InlineKeyboardButton("🔵 ₹25 — 270 Likes", callback_data='plan_25_270'),
        types.InlineKeyboardButton("🟣 ₹30 — 340 Likes", callback_data='plan_30_340'),
        types.InlineKeyboardButton("🟣 ₹35 — 415 Likes", callback_data='plan_35_415'),
        types.InlineKeyboardButton("🔥 ₹40 — 500 Likes", callback_data='plan_40_500'),
        types.InlineKeyboardButton("🔥 ₹45 — 585 Likes", callback_data='plan_45_585'),
        types.InlineKeyboardButton("🚀 ₹50 — 700 Likes (Best)", callback_data='plan_50_700')
    )

    text = (
        "🔥 **FREE FIRE DAILY LIKES SERVICE** 🔥\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ *Get fast, secure and genuine profile likes everyday.*\n\n"
        "💎 **CHOOSE YOUR PLAN BELOW:**\n"
        "*(Bade plans par zyada likes aur bada fayda milta hai!)*\n\n"
        "👇 *Apna pasandida plan select karne ke liye button dabayein:*"
    )
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

# Help & Trust Guide
@bot.message_handler(func=lambda message: message.text == "ℹ️ Help & Trust Guide")
def help_info(message):
    text = (
        "🛡️ **TRUST & SAFETY GUIDE**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "• **Garena Rules Safe:** 100 se zyada likes hone पर limit ke hisab se roz likes milti hain.\n"
        "• **Zero Ban Risk:** ID 100% safe rehti hai.\n"
        "• **Fast Support:** Payment ke baad turant UTR aur UID submit karein."
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=get_main_menu(message.from_user.id))

# Admin Dashboard
@bot.message_handler(func=lambda message: message.text == "👑 Admin Dashboard")
def admin_dashboard(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Unauthorized.", reply_markup=get_main_menu(message.from_user.id))
        return

    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders")
    count = cursor.fetchone()[0]
    conn.close()

    text = (
        "👑 **ADMIN CONTROL PANEL**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 Total Orders: `{count}`\n\n"
        "💻 *Command:* Type `/list` to view customer records with their Free Fire UIDs & Names."
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=get_main_menu(message.from_user.id))

# Plan Selection Handler
@bot.callback_query_handler(func=lambda call: call.data.startswith('plan_'))
def handle_plan_selection(call):
    parts = call.data.split('_')
    price_val = parts[1]
    likes_val = int(parts[2])
    
    price_str = f"₹{price_val}"
    likes_str = f"{likes_val} Likes"
    
    user_states[call.from_user.id] = {
        'state': 'waiting_for_utr', 
        'plan': f"{price_str} - {likes_str}",
        'last_msg_id': call.message.message_id
    }
    bot.answer_callback_query(call.id)

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📷 View QR Code", callback_data='show_qr'),
        types.InlineKeyboardButton("📋 Copy UPI ID", callback_data='show_upi')
    )

    if likes_val > 100:
        notice_text = (
            f"📦 **ORDER SUMMARY CARD (MEGA PACK)**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔹 **Plan:** `{price_str} — {likes_str}`\n"
            f"👤 **Name:** Santosh Rawat\n\n"
            f"⚠️ **Zaroori Suchna (100+ Likes Notice):**\n"
            f"Garena ke rules ke mutabiq ek din mein sirf **100 Likes** ki limit hoti hai. Isiliye aapko aaj 100 likes milenge aur bachi hui likes **agle din (next day)** aur phir uske agle din milti rahengi jab tak aapke saare likes poore nahi ho jaate. Isse aapki ID 100% safe rahegi!\n\n"
            f"👇 **Payment ke liye upar diye gaye kisi ek option par click karein:**"
        )
    else:
        notice_text = (
            f"📦 **ORDER SUMMARY CARD**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔹 **Plan:** `{price_str} — {likes_str}`\n"
            f"👤 **Name:** Santosh Rawat\n\n"
            f"🛡️ **Safety Guarantee:** Garena rules ke mutabiq secure delivery.\n\n"
            f"👇 **Payment ke liye upar diye gaye kisi ek option par click karein:**"
        )
    
    try:
        bot.edit_message_text(notice_text, call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
    except Exception:
        bot.send_message(call.message.chat.id, notice_text, parse_mode='Markdown', reply_markup=markup)

# Show QR Image with "Payment Ho Gaya" at bottom
@bot.callback_query_handler(func=lambda call: call.data == 'show_qr')
def send_qr_image(call):
    bot.answer_callback_query(call.id)
    safe_delete(call.message.chat.id, call.message.message_id)
    
    qr_url = "https://i.postimg.cc/kGQwSRy4/QR-Code.png"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Payment Ho Gaya (Send UTR)", callback_data='send_utr_prompt'))

    sent_msg = bot.send_photo(
        call.message.chat.id, 
        qr_url, 
        caption="📷 **SCAN & PAY VIA QR**\n━━━━━━━━━━━━━━━━━━━━━━━\n• Is QR code ko scan karke exact amount pay karein.\n• Payment karne ke baad **niche diye gaye button** par click karein.", 
        parse_mode='Markdown', 
        reply_markup=markup
    )
    if call.from_user.id in user_states:
        user_states[call.from_user.id]['active_step_msg'] = sent_msg.message_id

# Show UPI Details with "Payment Ho Gaya" at bottom
@bot.callback_query_handler(func=lambda call: call.data == 'show_upi')
def send_upi_details(call):
    bot.answer_callback_query(call.id)
    safe_delete(call.message.chat.id, call.message.message_id)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Payment Ho Gaya (Send UTR)", callback_data='send_utr_prompt'))

    upi_text = (
        "💳 **DIRECT UPI PAYMENT**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Aap niche di gayi UPI ID par seedha payment kar sakte hain:\n\n"
        "🆔 `santoshkumarram085-1@oksbi`\n"
        "👤 **Name:** Santosh Rawat\n\n"
        "*(Payment karne ke baad niche wale button par click karein)*"
    )
    sent_msg = bot.send_message(call.message.chat.id, upi_text, parse_mode='Markdown', reply_markup=markup)
    if call.from_user.id in user_states:
        user_states[call.from_user.id]['active_step_msg'] = sent_msg.message_id

# Prompt for UTR
@bot.callback_query_handler(func=lambda call: call.data == 'send_utr_prompt')
def prompt_utr(call):
    bot.answer_callback_query(call.id)
    safe_delete(call.message.chat.id, call.message.message_id)
    
    sent_msg = bot.send_message(
        call.message.chat.id,
        "📝 **ENTER TRANSACTION DETAILS**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Kripya apne payment ka **12-digit UTR / Transaction Number** yahan chat mein type karke bhejein:",
        parse_mode='Markdown'
    )
    if call.from_user.id in user_states:
        user_states[call.from_user.id]['utr_prompt_msg_id'] = sent_msg.message_id

# Handle Text Inputs (UTR -> UID Sequence with proper cleanup)
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    state = user_states.get(user_id)

    if isinstance(state, dict) and state.get('state') == 'waiting_for_utr':
        utr = message.text.strip()
        plan_selected = state.get('plan')
        
        safe_delete(message.chat.id, message.message_id)
        if 'utr_prompt_msg_id' in state:
            safe_delete(message.chat.id, state['utr_prompt_msg_id'])
        if 'active_step_msg' in state:
            safe_delete(message.chat.id, state['active_step_msg'])

        user_states[user_id] = {'state': 'waiting_for_uid', 'utr': utr, 'plan': plan_selected}

        sent_msg = bot.send_message(
            message.chat.id,
            "✅ **UTR RECEIVED SUCCESSFULLY!**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📦 Plan: `{plan_selected}`\n"
            f"🔢 UTR: `{utr}`\n\n"
            "🎯 **Aakhri Step:** Ab aap apna **Free Fire Game UID** yahan bhejein jahan likes bhejne hain:",
            parse_mode='Markdown'
        )
        user_states[user_id]['uid_prompt_msg_id'] = sent_msg.message_id

    elif isinstance(state, dict) and state.get('state') == 'waiting_for_uid':
        game_uid = message.text.strip()
        utr = state.get('utr')
        plan_selected = state.get('plan')
        username = message.from_user.username or message.from_user.first_name or "User"

        safe_delete(message.chat.id, message.message_id)
        if 'uid_prompt_msg_id' in state:
            safe_delete(message.chat.id, state['uid_prompt_msg_id'])

        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (user_id, username, plan_name, utr_number, game_uid, status) VALUES (?, ?, ?, ?, ?, ?)",
                       (user_id, username, plan_selected, utr, game_uid, 'Pending Verification'))
        conn.commit()
        conn.close()

        user_states.pop(user_id, None)

        bot.send_message(
            message.chat.id,
            "🎉 **CONGRATULATIONS! ORDER PLACED SUCCESSFULLY!**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📦 Plan: `{plan_selected}`\n"
            f"🆔 Game UID: `{game_uid}`\n"
            f"🔢 UTR: `{utr}`\n\n"
            "Admin dwara payment verify hote hi aapka daily likes process shuru kar diya jayega! 🚀",
            parse_mode='Markdown',
            reply_markup=get_main_menu(user_id)
        )
    else:
        bot.reply_to(message, "Kripya menu ka use karein ya /start dabayein.", reply_markup=get_main_menu(user_id))

# Admin Advanced List Command (/list) - Shows Name, Username, Plan, UTR & Game UID clearly
@bot.message_handler(commands=['list', 'export'])
def list_orders(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Unauthorized.")
        return

    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, username, plan_name, utr_number, game_uid, status FROM orders")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        bot.reply_to(message, "📂 Abhi tak koi order database mein nahi hai.", reply_markup=get_main_menu(message.from_user.id))
        return

    response = "📋 **CUSTOMER ORDERS & FREE FIRE UIDs:**\n━━━━━━━━━━━━━━━━━━━━━━━\n"
    for row in rows:
        response += (
            f"🔹 **Order ID:** `{row[0]}`\n"
            f"👤 **Customer:** @{row[2]} (ID: `{row[1]}`)\n"
            f"📦 **Plan:** {row[3]}\n"
            f"🆔 **Free Fire UID:** `{row[5]}`\n"
            f"🔢 **UTR:** `{row[4]}`\n"
            f"📌 **Status:** {row[6]}\n"
            f"----------------------------------\n"
        )

    if len(response) > 4000:
        for x in range(0, len(response), 4000):
            bot.send_message(message.chat.id, response[x:x+4000], parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, response, parse_mode='Markdown', reply_markup=get_main_menu(message.from_user.id))

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
