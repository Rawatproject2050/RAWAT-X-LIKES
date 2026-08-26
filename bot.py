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

# /start & Main Menu Handler - Plans hamesha upar active rahenge
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
        "• **Garena Rules Safe:** 100 se zyada likes hone par limit ke hisab se roz likes milti hain.\n"
        "• **Zero Ban Risk:** ID 100% safe rehti hai.\n"
        "• **Fast Support:** Payment ke baad turant UTR aur UID submit karein."
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=get_main_menu(message.from_user.id))

# Admin Dashboard - Professional Card Style with Pending Counts
@bot.message_handler(func=lambda message: message.text == "👑 Admin Dashboard")
def admin_dashboard(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Unauthorized.", reply_markup=get_main_menu(message.from_user.id))
        return

    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status='Pending Verification'")
    pending_count = cursor.fetchone()[0]
    conn.close()

    text = (
        "╔═══════════════════════╗\n"
        "   👑 **ADMIN CONTROL PANEL**\n"
        "╚═══════════════════════╝\n"
        f"📊 **Total Orders:** `{total_count}`\n"
        f"⏳ **Pending Verifications:** `{pending_count}`\n\n"
        "💡 *Note:* Jaise hi koi user UTR aur Free Fire UID bhejega, aapko ek professional verification card milega jisme Yes/No ka option hoga."
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=get_main_menu(message.from_user.id))

# Plan Selection Handler (Professional Card Style)
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

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📷 View QR Code", callback_data='show_qr'),
        types.InlineKeyboardButton("📋 Copy UPI ID", callback_data='show_upi')
    )

    if likes_val > 100:
        notice_text = (
            f"╔═══════════════════════╗\n"
            f"    📦 **ORDER SUMMARY CARD**\n"
            f"╚═══════════════════════╝\n"
            f"🔹 **Plan Selected:** `{price_str} — {likes_str}`\n"
            f"👤 **Pay To:** Santosh Rawat\n\n"
            f"⚠️ **Zaroori Suchna (100+ Likes Notice):**\n"
            f"Garena rules ke mutabiq ek din mein sirf **100 Likes** ki limit hoti hai. Isiliye aapko roz limit ke hisab se likes milti rahengi jab tak poore na ho jayein!\n\n"
            f"👇 **Payment ke liye option select karein:**"
        )
    else:
        notice_text = (
            f"╔═══════════════════════╗\n"
            f"    📦 **ORDER SUMMARY CARD**\n"
            f"╚═══════════════════════╝\n"
            f"🔹 **Plan Selected:** `{price_str} — {likes_str}`\n"
            f"👤 **Pay To:** Santosh Rawat\n\n"
            f"🛡️ **Safety Guarantee:** 100% Garena Safe Delivery.\n\n"
            f"👇 **Payment ke liye option select karein:**"
        )
    
    bot.send_message(call.message.chat.id, notice_text, parse_mode='Markdown', reply_markup=markup)

# Show QR Image with "Payment Ho Gaya" button
@bot.callback_query_handler(func=lambda call: call.data == 'show_qr')
def send_qr_image(call):
    bot.answer_callback_query(call.id)
    qr_url = "https://i.postimg.cc/kGQwSRy4/QR-Code.png"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Payment Ho Gaya (Send UTR)", callback_data='send_utr_prompt'))

    bot.send_photo(
        call.message.chat.id, 
        qr_url, 
        caption=(
            "╔═══════════════════════╗\n"
            "    📷 **QR CODE PAYMENT**\n"
            "╚═══════════════════════╝\n"
            "• Is QR code ko scan karke exact amount pay karein.\n"
            "• Payment karne ke baad niche diye gaye button par click karein."
        ), 
        parse_mode='Markdown', 
        reply_markup=markup
    )

# Show UPI Details with "Payment Ho Gaya" button
@bot.callback_query_handler(func=lambda call: call.data == 'show_upi')
def send_upi_details(call):
    bot.answer_callback_query(call.id)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Payment Ho Gaya (Send UTR)", callback_data='send_utr_prompt'))

    upi_text = (
        "╔═══════════════════════╗\n"
        "    💳 **DIRECT UPI PAYMENT**\n"
        "╚═══════════════════════╝\n"
        "Aap niche di gayi UPI ID par payment karein:\n\n"
        "🆔 `santoshkumarram085-1@oksbi`\n"
        "👤 **Name:** Santosh Rawat\n\n"
        "*(Payment karne ke baad niche wale button par click karein)*"
    )
    bot.send_message(call.message.chat.id, upi_text, parse_mode='Markdown', reply_markup=markup)

# Prompt for UTR
@bot.callback_query_handler(func=lambda call: call.data == 'send_utr_prompt')
def prompt_utr(call):
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        "╔═══════════════════════╗\n"
        "    📝 **ENTER TRANSACTION**\n"
        "╚═══════════════════════╝\n"
        "Kripya apne payment ka **12-digit UTR / Transaction Number** yahan chat mein type karke bhejein:",
        parse_mode='Markdown'
    )

# Handle Text Inputs (UTR -> UID Sequence)
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    # Admin ke menu buttons ko ignore karne ke liye
    if message.from_user.id == ADMIN_ID and message.text in ["🚀 Start Bot", "💎 Buy Likes & Pricing", "ℹ️ Help & Trust Guide", "👑 Admin Dashboard"]:
        return

    user_id = message.from_user.id
    state = user_states.get(user_id)

    if isinstance(state, dict) and state.get('state') == 'waiting_for_utr':
        utr = message.text.strip()
        user_states[user_id]['utr'] = utr
        user_states[user_id]['state'] = 'waiting_for_uid'

        bot.send_message(
            message.chat.id,
            "╔═══════════════════════╗\n"
            "    ✅ **UTR RECEIVED**\n"
            "╚═══════════════════════╝\n"
            f"🔢 UTR: `{utr}`\n\n"
            "🎯 **Aakhri Step:** Ab aap apna **Free Fire Game UID** yahan bhejein jahan likes bhejne hain:",
            parse_mode='Markdown'
        )

    elif isinstance(state, dict) and state.get('state') == 'waiting_for_uid':
        game_uid = message.text.strip()
        utr = state.get('utr')
        plan_selected = state.get('plan')
        username = message.from_user.username or message.from_user.first_name or "User"

        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (user_id, username, plan_name, utr_number, game_uid, status) VALUES (?, ?, ?, ?, ?, ?)",
                       (user_id, username, plan_selected, utr, game_uid, 'Pending Verification'))
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()

        user_states.pop(user_id, None)

        # User ko confirmation message
        bot.send_message(
            message.chat.id,
            "╔═══════════════════════╗\n"
            "  🎉 **ORDER SUBMITTED!**\n"
            "╚═══════════════════════╝\n"
            f"📦 Plan: `{plan_selected}`\n"
            f"🆔 Game UID: `{game_uid}`\n"
            f"🔢 UTR: `{utr}`\n\n"
            "Aapka order verification ke liye Admin ke paas bhej diya gaya hai. Thodi der mein verify ho jayega! 🚀",
            parse_mode='Markdown',
            reply_markup=get_main_menu(user_id)
        )

        # 👑 ADMIN KE LIYE TAGRA PROFESSIONAL VERIFICATION CARD WITH YES / NO BUTTONS
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("✅ Yes (Approve)", callback_data=f"approve_{order_id}_{user_id}"),
            types.InlineKeyboardButton("❌ No (Reject)", callback_data=f"reject_{order_id}_{user_id}")
        )

        admin_card = (
            "╔═══════════════════════╗\n"
            "    🚨 **NEW UTR VERIFICATION**\n"
            "╚═══════════════════════╝\n"
            f"🔹 **Order ID:** `{order_id}`\n"
            f"👤 **Customer Name:** `{username}`\n"
            f"💬 **Username:** @{username}\n"
            f"🆔 **Telegram ID:** `{user_id}`\n"
            f"📦 **Selected Plan:** `{plan_selected}`\n"
            f"🎮 **Free Fire UID:** `{game_uid}`\n"
            f"🔢 **UTR Number:** `{utr}`\n\n"
            "👇 *Kripya UTR check karein aur niche decision lein:*"
        )
        bot.send_message(ADMIN_ID, admin_card, parse_mode='Markdown', reply_markup=admin_markup)

    else:
        if message.from_user.id != ADMIN_ID:
            bot.reply_to(message, "Kripya menu ka use karein ya /start dabayein.", reply_markup=get_main_menu(user_id))

# Admin Approval / Rejection Handler
@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_') or call.data.startswith('reject_'))
def handle_admin_verification(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Aap admin nahi hain!", show_alert=True)
        return

    parts = call.data.split('_')
    action = parts[0]
    order_id = parts[1]
    target_user_id = int(parts[2])

    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()

    if action == 'approve':
        cursor.execute("UPDATE orders SET status = 'Approved' WHERE id = ?", (order_id,))
        conn.commit()
        conn.close()

        bot.answer_callback_query(call.id, "Order Approved Successfully!")
        
        # Admin card ko update karke status dikhana
        try:
            bot.edit_message_text(
                text=call.message.text + "\n\n✅ **STATUS: APPROVED BY ADMIN**",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode='Markdown'
            )
        except Exception:
            pass

        # User ke paas Congratulations SMS bhejna
        bot.send_message(
            target_user_id,
            "╔═══════════════════════╗\n"
            "  🎉 **CONGRATULATIONS!**\n"
            "╚═══════════════════════╝\n"
            "Badhai ho! Aapka UTR successfully verify ho gaya hai. Aapke Free Fire account par likes bhejne ki process shuru kar di gayi hai! 🚀🔥",
            parse_mode='Markdown'
        )

    elif action == 'reject':
        cursor.execute("UPDATE orders SET status = 'Rejected' WHERE id = ?", (order_id,))
        conn.commit()
        conn.close()

        bot.answer_callback_query(call.id, "Order Rejected.")
        
        # Admin card ko update karke status dikhana
        try:
            bot.edit_message_text(
                text=call.message.text + "\n\n❌ **STATUS: REJECTED BY ADMIN**",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode='Markdown'
            )
        except Exception:
            pass

        # User ke paas Rejection / Correction SMS bhejna
        bot.send_message(
            target_user_id,
            "╔═══════════════════════╗\n"
            "  ❌ **VERIFICATION FAILED**\n"
            "╚═══════════════════════╝\n"
            "Khed hai, aapka UTR match nahi hua ya galat pay kiya gaya hai. Kripya apna payment dobara check karein ya sahi UTR ke sath naya order dalein.",
            parse_mode='Markdown'
        )

# Flask Web Service Server for Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Professional Tagra Bot Web Service is Live!"

def run_flask():
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    print("Professional Bot & Web Service running...")
    bot.infinity_polling()
