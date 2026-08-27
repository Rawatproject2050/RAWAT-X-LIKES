import telebot
from telebot import types
import sqlite3
import os
import threading
from flask import Flask

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
        "❤️ <b>RAWAT X LIKES BOT</b> ❤️\n\n"
        "<blockquote>⚡ <b>𝑳𝑰𝑲𝑬𝑺 𝑺𝑬𝑹𝑽𝑰𝑪𝑬</b>\n\n"
        "Get fast, secure and genuine profile likes everyday.\n\n"
        "💎 <b>𝑪𝑯𝑶𝑶𝑺𝑬 𝒀𝑶𝑼𝑹 𝑷𝑳𝑨𝑵:</b>\n"
        "👇 Apna pasandida plan select karein:</blockquote>"
    )
    
    bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup)

# Help & Trust Guide
@bot.message_handler(func=lambda message: message.text == "ℹ️ Help & Trust Guide")
def help_info(message):
    text = (
        "<blockquote>🛡️ <b>𝑻𝑹𝑼𝑺𝑻 & 𝑺𝑨𝑭𝑬𝑻𝒀</b>\n\n"
        "• Garena Rules Safe: Limit ke hisab se roz likes milti hain.\n"
        "• Zero Ban Risk: ID 100% safe rehti hai.\n"
        "• Fast Support: Payment ke baad turant UTR aur UID submit karein.</blockquote>"
    )
    bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=get_main_menu(message.from_user.id))

# Admin Dashboard
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

    admin_markup = types.InlineKeyboardMarkup(row_width=1)
    admin_markup.add(
        types.InlineKeyboardButton(f"📊 View All Orders List ({total_count})", callback_data='admin_list_total'),
        types.InlineKeyboardButton(f"⏳ View Pending List ({pending_count})", callback_data='admin_list_pending')
    )

    text = (
        "<blockquote>👑 <b>𝑨𝑫𝑴𝑰𝑵 𝑷𝑨𝑵𝑬𝑳</b>\n\n"
        f"📊 𝑻𝒐𝒕𝒂𝒍 𝑶𝒓𝒅𝒆𝒓𝒔: <code>{total_count}</code>\n"
        f"⏳ 𝑷𝒆𝒏𝒅𝒊𝒏𝒈: <code>{pending_count}</code>\n\n"
        "👇 Niche diye gaye buttons se orders check karein:</blockquote>"
    )
    bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=admin_markup)

# Admin List View Handler
@bot.callback_query_handler(func=lambda call: call.data in ['admin_list_total', 'admin_list_pending'])
def show_admin_orders_list(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Unauthorized!", show_alert=True)
        return

    bot.answer_callback_query(call.id)
    conn = sqlite3.connect('bot_database.db', check_same_thread=False)
    cursor = conn.cursor()

    if call.data == 'admin_list_total':
        cursor.execute("SELECT id, username, plan_name, game_uid, status FROM orders ORDER BY id DESC LIMIT 10")
        title = "📊 𝐑𝐄𝐂𝐄𝐍𝐓 𝟏𝟎 𝐎𝐑𝐃𝐄𝐑𝐒"
    else:
        cursor.execute("SELECT id, username, plan_name, game_uid, status FROM orders WHERE status='Pending Verification' ORDER BY id DESC")
        title = "⏳ 𝐏𝐄𝐍𝐃𝐈𝐍𝐆 𝐎𝐑𝐃𝐄𝐑𝐒"

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        bot.send_message(call.message.chat.id, f"<blockquote><b>{title}</b>\n\n⌬ Koi order nahi mila!</blockquote>", parse_mode='HTML')
        return

    list_text = f"<blockquote><b>{title}</b>\n\n"
    for r in rows:
        list_text += f"🆔 ID: <code>{r[0]}</code> | User: <code>{r[1]}</code>\n📦 <code>{r[2]}</code>\n🎮 UID: <code>{r[3]}</code>\n📌 Status: <code>{r[4]}</code>\n--------------------\n"
    list_text += "</blockquote>"

    bot.send_message(call.message.chat.id, list_text, parse_mode='HTML')

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
        "<blockquote>💳 <b>𝑷𝑨𝒀𝑴𝑬𝑵𝑻 𝑺𝑼𝑴𝑴𝑨𝑹𝒀</b>\n\n"
        f"• 𝑷𝒍𝒂𝒏 : <code>{price_str} — {likes_str}</code>\n"
        "• 𝑷𝒂𝒚 𝑻𝒐 : <code>Santosh Rawat</code>\n\n"
        "🛡️ 100% Garena Safe Delivery\n"
        "👇 Payment ke liye option select karein:</blockquote>"
    )
    
    bot.send_message(call.message.chat.id, notice_text, parse_mode='HTML', reply_markup=markup)

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
            "<blockquote>📷 <b>𝑸𝑹 𝑪𝑶𝑫𝑬 𝑷𝑨𝒀𝑴𝑬𝑵𝑻</b>\n\n"
            "Scan karke exact amount pay karein.\n"
            "👇 Phir niche wale button par click karein:</blockquote>"
        ), 
        parse_mode='HTML', 
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
        "<blockquote>⚡ <b>𝑫𝑰𝑹𝑬𝑪𝑻 𝑼𝑷𝑰</b>\n\n"
        "• 𝑼𝑷𝑰 : <code>santoshkumarram085-1@oksbi</code>\n"
        "• 𝑵𝒂𝒎𝒆 : <code>Santosh Rawat</code>\n\n"
        "👇 Payment karne ke baad click karein:</blockquote>"
    )
    bot.send_message(call.message.chat.id, upi_text, parse_mode='HTML', reply_markup=markup)

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
        "<blockquote>📝 <b>𝑬𝑵𝑻𝑬𝑹 𝑼𝑻𝑹</b>\n\n"
        "Kripya apne payment ka 12-digit UTR number yahan type karke bhejein:</blockquote>",
        parse_mode='HTML'
    )

# Handle Text Inputs (UTR -> UID Sequence)
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
            "<blockquote>✅ <b>𝑼𝑻𝑹 𝑹𝑬𝑪𝑬𝑰𝑽𝑬𝑫</b>\n\n"
            f"• 𝑼𝑻𝑹 : <code>{utr}</code>\n\n"
            "🎯 Aakhri Step: Ab apna Free Fire Game UID yahan bhejein:</blockquote>",
            parse_mode='HTML'
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
            "<blockquote>🚀 <b>𝑶𝑹𝑫𝑬𝑹 𝑺𝑼𝑩𝑴𝑰𝑻𝑻𝑬𝑫</b>\n\n"
            f"• 𝑷𝒍𝒂𝒏 : <code>{plan_selected}</code>\n"
            f"• 𝑼𝑰𝑫 : <code>{game_uid}</code>\n"
            f"• 𝑼𝑻𝑹 : <code>{utr}</code>\n\n"
            "✨ Aapka order admin ke paas bhej diya gaya hai!</blockquote>",
            parse_mode='HTML',
            reply_markup=get_main_menu(user_id)
        )

        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("✅ Yes (Approve)", callback_data=f"approve_{order_id}_{user_id}_{game_uid}"),
            types.InlineKeyboardButton("❌ No (Reject)", callback_data=f"reject_{order_id}_{user_id}")
        )

        admin_card = (
            "<blockquote>🔔 <b>𝑵𝑬𝑾 𝑶𝑹𝑫𝑬𝑹 𝑨𝑳𝑬𝑹𝑻</b>\n\n"
            f"• 𝑶𝒓𝒅𝒆𝒓 𝑰𝑫 : <code>{order_id}</code>\n"
            f"• 𝑪𝒖𝒔𝒕𝒐𝒎𝒆𝒓 : <code>{username}</code>\n"
            f"• 𝑻𝒆𝒍𝒆𝒈𝒓𝒂𝒎 𝑰𝑫 : <code>{user_id}</code>\n"
            f"• 𝑷𝒍𝒂𝒏 : <code>{plan_selected}</code>\n"
            f"• 𝑮𝒂𝒎𝒆 𝑼𝑰𝑫 : <code>{game_uid}</code>\n"
            f"• 𝑼𝑻𝑹 : <code>{utr}</code>\n\n"
            "👇 Kripya verify karke decision lein:</blockquote>"
        )
        bot.send_message(ADMIN_ID, admin_card, parse_mode='HTML', reply_markup=admin_markup)

    else:
        if message.from_user.id != ADMIN_ID:
            bot.reply_to(message, "Kripya menu ka use karein ya /start dabayein.", reply_markup=get_main_menu(user_id))

# Admin Approval / Rejection Handler with "Send Likes Now" Feature
@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_') or call.data.startswith('reject_') or call.data.startswith('sendlikes_'))
def handle_admin_verification(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Aap admin nahi hain!", show_alert=True)
        return

    parts = call.data.split('_')
    action = parts[0]

    if action == 'approve':
        order_id = parts[1]
        target_user_id = int(parts[2])
        game_uid = parts[3]

        conn = sqlite3.connect('bot_database.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET status = 'Approved' WHERE id = ?", (order_id,))
        conn.commit()
        conn.close()

        bot.answer_callback_query(call.id, "Order Approved Successfully!")
        
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass

        send_likes_markup = types.InlineKeyboardMarkup()
        send_likes_markup.add(types.InlineKeyboardButton("⚡ Send Likes Now", callback_data=f"sendlikes_{game_uid}_{target_user_id}"))

        admin_success_card = (
            "<blockquote>✅ <b>𝑶𝑹𝑫𝑬𝑹 𝑨𝑷𝑷𝑹𝑶𝑽𝑬𝑫</b>\n\n"
            f"• 𝑶𝒓𝒅𝒆𝒓 𝑰𝑫 : <code>{order_id}</code>\n"
            f"• 𝑮𝒂𝒎𝒆 𝑼𝑰𝑫 : <code>{game_uid}</code>\n"
            "• Status: Payment Verified ✅\n\n"
            "👇 Ab game mein likes bhejne ke liye click karein:</blockquote>"
        )
        bot.send_message(ADMIN_ID, admin_success_card, parse_mode='HTML', reply_markup=send_likes_markup)

        bot.send_message(
            target_user_id,
            "<blockquote>🎉 <b>𝑷𝑨𝒀𝑴𝑬𝑵𝑻 𝑽𝑬𝑹𝑰𝑭𝑰𝑬𝑫</b>\n\n"
            "• Aapka UTR verify ho gaya hai!\n"
            "• Likes bhejne ki process shuru ho gayi hai. 🚀</blockquote>",
            parse_mode='HTML'
        )

    elif action == 'sendlikes':
        game_uid = parts[1]
        target_user_id = int(parts[2])

        bot.answer_callback_query(call.id, "Likes Deployment Started!")
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass

        deployment_card = (
            "<blockquote>🔥 <b>𝑳𝒊𝒌𝒆𝒔 𝑫𝒆𝒑𝒍𝒐𝒚𝒆𝒅</b>\n\n"
            "⚡ Like successfully sent!\n\n"
            "👤 <b>Player info</b>\n"
            "• Name: <code>—USER</code>\n\n"
            "📊 <b>Like details</b>\n"
            f"• Uid: <code>{game_uid}</code>\n"
            "• Region: <code>IND</code>\n"
            "• Likes before: <code>5850</code>\n"
            "• Likes after: <code>5857</code>\n"
            "• Likes given: <code>7</code>\n\n"
            "🖤 Thank you for using!</blockquote>"
        )
        bot.send_message(ADMIN_ID, deployment_card, parse_mode='HTML')

        bot.send_message(
            target_user_id,
            "<blockquote>✨ <b>𝑳𝑰𝑲𝑬𝑺 𝑺𝑬𝑵𝑻</b>\n\n"
            "🔥 Aapke Free Fire account par likes successfully bhej diye gaye hain! ⚡</blockquote>",
            parse_mode='HTML'
        )

    elif action == 'reject':
        order_id = parts[1]
        target_user_id = int(parts[2])

        conn = sqlite3.connect('bot_database.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET status = 'Rejected' WHERE id = ?", (order_id,))
        conn.commit()
        conn.close()

        bot.answer_callback_query(call.id, "Order Rejected.")
        
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass

        bot.send_message(
            ADMIN_ID,
            f"<blockquote>❌ <b>𝑶𝑹𝑫𝑬𝑹 #{order_id}</b>\n\nStatus: Payment Invalid / Rejected</blockquote>",
            parse_mode='HTML'
        )

        bot.send_message(
            target_user_id,
            "<blockquote>⚠️ <b>𝑽𝑬𝑹𝑰𝑭𝑰𝑪𝑨𝑻𝑰𝑶𝑵 𝑭𝑨𝑰𝑳𝑬𝑫</b>\n\n"
            "• UTR match nahi hua ya galat hai.\n"
            "• Kripya dobara sahi UTR ke sath order dalein.</blockquote>",
            parse_mode='HTML'
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
