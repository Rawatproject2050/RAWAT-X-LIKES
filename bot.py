import telebot
from telebot import types
import sqlite3
import os
import threading
from flask import Flask

# Render Environment Variables se securely uthayega
TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
ADMIN_ID = int(os.getenv('ADMIN_ID', '6665529050'))

bot = telebot.TeleBot(TOKEN)

# Database Setup
def init_db():
    conn = sqlite3.connect('bot_database.db', check_same_thread=False)
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

# Dynamic Keyboard: Admin ke liye sirf dashboard, baaki users ke liye normal menu
def get_main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if user_id == ADMIN_ID:
        markup.add(types.KeyboardButton("👑 Admin Dashboard"))
    else:
        markup.add(
            types.KeyboardButton("🚀 Start Bot"),
            types.KeyboardButton("💎 Buy Likes & Pricing"),
            types.KeyboardButton("ℹ️ Help & Trust Guide")
        )
    return markup

# /start & Main Menu Handler
@bot.message_handler(commands=['start'])
@bot.message_handler(func=lambda message: message.text in ["🚀 Start Bot", "💎 Buy Likes & Pricing"])
def send_welcome(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except Exception:
        pass

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
        "𖣠 𝑳𝒊𝒌𝒆𝒔 𝑺𝒆𝒓𝒗𝒊𝒄𝒆 𖣠\n"
        "╭╌╌╌╌╌╌╌╌╌╌╌╮\n"
        "⌬ *Get fast, secure and genuine profile likes everyday.*\n"
        "╰╌╌╌╌╌╌╌╌╌╌╌╯\n\n"
        "💎 **𝑪𝑯𝑶𝑶𝑺𝑬 𝒀𝑶𝑼𝑹 𝑷𝑳𝑨𝑵:**\n"
        "👇 *Apna pasandida plan select karein:*"
    )
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

# Help & Trust Guide
@bot.message_handler(func=lambda message: message.text == "ℹ️ Help & Trust Guide")
def help_info(message):
    text = (
        "𖣠 𝑻𝒓𝒖𝒔𝒕 & 𝑺𝒂𝒇𝒆𝒕𝒚 𖣠\n"
        "╭╌╌╌╌╌╌╌╌╌╌╌╮\n"
        "⌬ **Garena Rules Safe:** Limit ke hisab se roz likes milti hain.\n"
        "⌬ **Zero Ban Risk:** ID 100% safe rehti hai.\n"
        "⌬ **Fast Support:** Payment ke baad turant UTR aur UID submit karein.\n"
        "╰╌╌╌╌╌╌╌╌╌╌╌╯"
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=get_main_menu(message.from_user.id))

# Admin Dashboard (Sirf Admin ko dikhega)
@bot.message_handler(func=lambda message: message.text == "👑 Admin Dashboard")
def admin_dashboard(message):
    if message.from_user.id != ADMIN_ID:
        return

    conn = sqlite3.connect('bot_database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status='Pending Verification'")
    pending_count = cursor.fetchone()[0]
    conn.close()

    text = (
        "𖣠 𝑨𝒅𝒎𝒊𝒏 𝑷𝒂𝒏𝒆𝒍 𖣠\n"
        "╭╌╌╌╌╌╌╌╌╌╌╌╮\n"
        f"📊 **𝑻𝒐𝒕𝒂𝒍 𝑶𝒓𝒅𝒆𝒓𝒔:** `{total_count}`\n"
        f"⏳ **𝑷𝒆𝒏𝒅𝒊𝒏𝒈 𝑽𝒆𝒓𝒊𝒇𝒊𝒄𝒂𝒕𝒊𝒐𝒏𝒔:** `{pending_count}`\n"
        "╰╌╌╌╌╌╌╌╌╌╌╌╯\n\n"
        "💡 *Note:* Jaise hi koi user UTR aur UID bhejega, aapko stylish card mil jayega."
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
        'plan': f"{price_str} - {likes_str}"
    }
    bot.answer_callback_query(call.id)

    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📷 View QR Code", callback_data='show_qr'),
        types.InlineKeyboardButton("📋 Copy UPI ID", callback_data='show_upi')
    )

    notice_text = (
        "𖣠 𝑶𝒓𝒅𝒆𝒓 𝑺𝒖𝒎𝒎𝒂𝒓𝒚 𖣠\n"
        "╭╌╌╌╌╌╌╌╌╌╌╌╮\n"
        f"⌬ 𝑷𝒍𝒂𝒏 : `{price_str} — {likes_str}`\n"
        f"⌬ 𝑷𝒂𝒚 𝑻𝒐 : `Santosh Rawat`\n"
        "╰╌╌╌╌╌╌╌╌╌╌╌╯\n\n"
        "🛡️ *100% Garena Safe Delivery*\n"
        "👇 **Payment ke liye option select karein:**"
    )
    
    bot.send_message(call.message.chat.id, notice_text, parse_mode='Markdown', reply_markup=markup)

# Show QR Image
@bot.callback_query_handler(func=lambda call: call.data == 'show_qr')
def send_qr_image(call):
    bot.answer_callback_query(call.id)
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass

    qr_url = "https://i.postimg.cc/kGQwSRy4/QR-Code.png"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Payment Ho Gaya (Send UTR)", callback_data='send_utr_prompt'))

    bot.send_photo(
        call.message.chat.id, 
        qr_url, 
        caption=(
            "𖣠 𝑸𝑹 𝑪𝑶𝑫𝑬 𝑷𝑨𝒀𝑴𝑬𝑵𝑻 𖣠\n"
            "╭╌╌╌╌╌╌╌╌╌╌╌╮\n"
            "⌬ Scan karke exact amount pay karein.\n"
            "╰╌╌╌╌╌╌╌╌╌╌╌╯"
        ), 
        parse_mode='Markdown', 
        reply_markup=markup
    )

# Show UPI Details
@bot.callback_query_handler(func=lambda call: call.data == 'show_upi')
def send_upi_details(call):
    bot.answer_callback_query(call.id)
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Payment Ho Gaya (Send UTR)", callback_data='send_utr_prompt'))

    upi_text = (
        "𖣠 𝑫𝑰𝑹𝑬𝑪𝑻 𝑼𝑷𝑰 𖣠\n"
        "╭╌╌╌╌╌╌╌╌╌╌╌╮\n"
        "⌬ 𝑼𝑷𝑰 : `santoshkumarram085-1@oksbi`\n"
        "⌬ 𝑵𝒂𝒎𝒆 : `Santosh Rawat`\n"
        "╰╌╌╌╌╌╌╌╌╌╌╌╯"
    )
    bot.send_message(call.message.chat.id, upi_text, parse_mode='Markdown', reply_markup=markup)

# Prompt for UTR
@bot.callback_query_handler(func=lambda call: call.data == 'send_utr_prompt')
def prompt_utr(call):
    bot.answer_callback_query(call.id)
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass

    bot.send_message(
        call.message.chat.id,
        "𖣠 𝑬𝑵𝑻𝑬𝑹 𝑼𝑻𝑹 𖣠\n"
        "╭╌╌╌╌╌╌╌╌╌╌╌╮\n"
        "⌬ Kripya 12-digit UTR number yahan bhejein:\n"
        "╰╌╌╌╌╌╌╌╌╌╌╌╯",
        parse_mode='Markdown'
    )

# Handle Text Inputs (UTR -> UID Sequence with Auto-Clean)
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.from_user.id == ADMIN_ID and message.text in ["👑 Admin Dashboard"]:
        return

    user_id = message.from_user.id
    state = user_states.get(user_id)

    if isinstance(state, dict) and state.get('state') == 'waiting_for_utr':
        utr = message.text.strip()
        user_states[user_id]['utr'] = utr
        user_states[user_id]['state'] = 'waiting_for_uid'

        try:
            bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            pass

        bot.send_message(
            message.chat.id,
            "𖣠 𝑼𝑻𝑹 𝑹𝑬𝑪𝑬𝑰𝑽𝑬𝑫 𖣠\n"
            "╭╌╌╌╌╌╌╌╌╌╌╌╮\n"
            f"⌬ 𝑼𝑻𝑹 : `{utr}`\n"
            "╰╌╌╌╌╌╌╌╌╌╌╌╯\n\n"
            "🎯 **Aakhri Step:** Ab apna **Free Fire Game UID** yahan bhejein:",
            parse_mode='Markdown'
        )

    elif isinstance(state, dict) and state.get('state') == 'waiting_for_uid':
        game_uid = message.text.strip()
        utr = state.get('utr')
        plan_selected = state.get('plan')
        username = message.from_user.username or message.from_user.first_name or "User"

        try:
            bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            pass

        conn = sqlite3.connect('bot_database.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO orders (user_id, username, plan_name, utr_number, game_uid, status) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, username, plan_selected, utr, game_uid, 'Pending Verification')
        )
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()

        user_states.pop(user_id, None)

        bot.send_message(
            message.chat.id,
            "𖣠 𝑶𝑹𝑫𝑬𝑹 𝑺𝑼𝑩𝑴𝑰𝑻𝑻𝑬𝑫 𖣠\n"
            "╭╌╌╌╌╌╌╌╌╌╌╌╮\n"
            f"⌬ 𝑷𝒍𝒂𝒏 : `{plan_selected}`\n"
            f"⌬ 𝑼𝑰𝑫 : `{game_uid}`\n"
            f"⌬ 𝑼𝑻𝑹 : `{utr}`\n"
            "╰╌╌╌╌╌╌╌╌╌╌╌╯\n\n"
            "Aapka order verification ke liye Admin ke paas bhej diya gaya hai! 🚀",
            parse_mode='Markdown',
            reply_markup=get_main_menu(user_id)
        )

        # 👑 ADMIN KE LIYE TAGRA STYLISH VERIFICATION CARD WITH YES/NO BUTTONS
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("✅ Yes (Approve)", callback_data=f"approve_{order_id}_{user_id}"),
            types.InlineKeyboardButton("❌ No (Reject)", callback_data=f"reject_{order_id}_{user_id}")
        )

        admin_card = (
            "𖣠 𝑵𝑬𝑾 𝑼𝑻𝑹 𝑽𝑬𝑹𝑰𝑭𝑰𝑪𝑨𝑻𝑰𝑶𝑵 𖣠\n"
            "╭╌╌╌╌╌╌╌╌╌╌╌╮\n"
            f"⌬ 𝑶𝒓𝒅𝒆𝒓 𝑰𝑫 : `{order_id}`\n"
            f"⌬ 𝑪𝒖𝒔𝒕𝒐𝒎𝒆𝒓 : `{username}`\n"
            f"⌬ 𝑻𝒆𝒍𝒆𝒈𝒓𝒂𝒎 𝑰𝑫 : `{user_id}`\n"
            f"⌬ 𝑷𝒍𝒂𝒏 : `{plan_selected}`\n"
            f"⌬ 𝑮𝒂𝒎𝒆 𝑼𝑰𝑫 : `{game_uid}`\n"
            f"⌬ 𝑼𝑻𝑹 : `{utr}`\n"
            "╰╌╌╌╌╌╌╌╌╌╌╌╯\n\n"
            "👇 *Kripya verify karke decision lein:*"
        )
        bot.send_message(ADMIN_ID, admin_card, parse_mode='Markdown', reply_markup=admin_markup)

    else:
        if message.from_user.id != ADMIN_ID:
            bot.reply_to(message, "Kripya menu ka use karein ya /start dabayein.", reply_markup=get_main_menu(user_id))

# Admin Approval / Rejection Handler (Card Gayab Ho Jayega)
@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_') or call.data.startswith('reject_'))
def handle_admin_verification(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Aap admin nahi hain!", show_alert=True)
        return

    parts = call.data.split('_')
    action = parts[0]
    order_id = parts[1]
    target_user_id = int(parts[2])

    conn = sqlite3.connect('bot_database.db', check_same_thread=False)
    cursor = conn.cursor()

    if action == 'approve':
        cursor.execute("UPDATE orders SET status = 'Approved' WHERE id = ?", (order_id,))
        conn.commit()
        conn.close()

        bot.answer_callback_query(call.id, "Order Approved Successfully!")
        
        # Admin card ko delete karke clean update dena
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass

        bot.send_message(
            ADMIN_ID,
            f"𖣠 𝑶𝑹𝑫𝑬𝑹 #{order_id} 𝑨𝑷𝑷𝑹𝑶𝑽𝑬𝑫 ✅",
            parse_mode='Markdown'
        )

        bot.send_message(
            target_user_id,
            "𖣠 𝑪𝑶𝑵𝑮𝑹𝑨𝑻𝑼𝑳𝑨𝑻𝑰𝑶𝑵𝑺 𖣠\n"
            "╭╌╌╌╌╌╌╌╌╌╌╌╮\n"
            "⌬ Aapka UTR verify ho gaya hai!\n"
            "⌬ Likes bhejne ki process shuru ho gayi hai. 🚀\n"
            "╰╌╌╌╌╌╌╌╌╌╌╌╯",
            parse_mode='Markdown'
        )

    elif action == 'reject':
        cursor.execute("UPDATE orders SET status = 'Rejected' WHERE id = ?", (order_id,))
        conn.commit()
        conn.close()

        bot.answer_callback_query(call.id, "Order Rejected.")
        
        # Admin card ko delete karke clean update dena
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass

        bot.send_message(
            ADMIN_ID,
            f"𖣠 𝑶𝑹𝑫𝑬𝑹 #{order_id} 𝑹𝑬𝑱𝑬𝑪𝑻𝑬𝑫 ❌",
            parse_mode='Markdown'
        )

        bot.send_message(
            target_user_id,
            "𖣠 𝑽𝑬𝑿𝑰𝑭𝑰𝑪𝑨𝑻𝑰𝑶𝑵 𝑭𝑨𝑰𝑳𝑬𝑫 𖣠\n"
            "╭╌╌╌╌╌╌╌╌╌╌╌╮\n"
            "⌬ UTR match nahi hua ya galat hai.\n"
            "⌬ Kripya dobara sahi UTR ke sath order dalein.\n"
            "╰╌╌╌╌╌╌╌╌╌╌╌╯",
            parse_mode='Markdown'
        )

# Flask Server for Render Keep-Alive
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Active and Running smoothly!"

def run_flask():
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    print("Bot & Web Server successfully started...")
    bot.infinity_polling()
