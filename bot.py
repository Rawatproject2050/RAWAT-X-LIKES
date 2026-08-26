import telebot
from telebot import types
import sqlite3
import os

# Render ke environment variable se token uthayega (Secure method)
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

# Temporary storage for user states
user_states = {}

# Persistent Menu Keyboard (Chat box ke paas button)
def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_start = types.KeyboardButton("🚀 Start Bot")
    btn_plans = types.KeyboardButton("💎 Buy Likes & Pricing")
    btn_help = types.KeyboardButton("ℹ️ Help & Trust Guide")
    btn_admin = types.KeyboardButton("👑 Admin Dashboard")
    markup.add(btn_start, btn_plans, btn_help, btn_admin)
    return markup

# /start command & Main Menu handler
@bot.message_handler(commands=['start'])
@bot.message_handler(func=lambda message: message.text in ["🚀 Start Bot", "💎 Buy Likes & Pricing"])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    
    # Pricing Buttons (Jo aapne bataye the)
    markup.add(types.InlineKeyboardButton("🟢 ₹5 — 40 Likes (Trial)", callback_data='plan_5'))
    markup.add(types.InlineKeyboardButton("🟡 ₹10 — 90 Likes", callback_data='plan_10'))
    markup.add(types.InlineKeyboardButton("🟡 ₹15 — 145 Likes", callback_data='plan_15'))
    markup.add(types.InlineKeyboardButton("🔵 ₹20 — 205 Likes", callback_data='plan_20'))
    markup.add(types.InlineKeyboardButton("🔵 ₹25 — 270 Likes", callback_data='plan_25'))
    markup.add(types.InlineKeyboardButton("🟣 ₹30 — 340 Likes", callback_data='plan_30'))
    markup.add(types.InlineKeyboardButton("🟣 ₹35 — 415 Likes", callback_data='plan_35'))
    markup.add(types.InlineKeyboardButton("🔥 ₹40 — 500 Likes (Mega Pack)", callback_data='plan_40'))
    markup.add(types.InlineKeyboardButton("🔥 ₹45 — 585 Likes", callback_data='plan_45'))
    markup.add(types.InlineKeyboardButton("🚀 ₹50 — 700 Likes (Best Value)", callback_data='plan_50'))

    welcome_text = (
        "🔥 **Welcome to Trusted Free Fire Daily Likes Service!** 🔥\n\n"
        "Get genuine likes for your profile everyday reliably and securely with 100% safety guarantee!\n\n"
        "💎 **Select Your Preferred Plan Below:**\n"
        "*(Bade plans par aapko zyada likes ka fayda milta hai!)*\n\n"
        "🛡️ **100% Safe & Trusted:** Hum Garena ke rules ke mutabiq chalte hain taaki aapki ID bilkul safe rahe."
    )
    
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown', reply_markup=get_main_menu())
    bot.send_message(message.chat.id, "👇 Neeche diye gaye plans mein se apna plan chunein:", reply_markup=markup)

# Help & Trust Guide Handler
@bot.message_handler(func=lambda message: message.text == "ℹ️ Help & Trust Guide")
def help_info(message):
    help_text = (
        "🛡️ **Why Trust Us? (Safety & Rules)**\n\n"
        "• **Garena Rules Followed:** Hum ek din mein ek limit (jaise 100 likes) ke hisab se likes provide karte hain, bachi hui likes agle din milti hain.\n"
        "• **Zero Risk:** Is method se aapki Free Fire ID ban hone ka koi khatra nahi rehta.\n"
        "• **Secure Payment:** Aap diye gaye QR code ya UPI ID par payment karke apna UTR aur UID bhej sakte hain."
    )
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown', reply_markup=get_main_menu())

# Admin Dashboard Handler
@bot.message_handler(func=lambda message: message.text == "👑 Admin Dashboard")
def admin_dashboard(message):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders")
    count = cursor.fetchone()[0]
    conn.close()

    admin_text = (
        "👑 **Admin Dashboard**\n\n"
        f"📊 Total Orders Received: `{count}`\n\n"
        "Commands:\n"
        "• Type `/list` to view all customer UTR and UID details."
    )
    bot.send_message(message.chat.id, admin_text, parse_mode='Markdown', reply_markup=get_main_menu())

# Handle Plan Selection & Safety Notification
@bot.callback_query_handler(func=lambda call: call.data.startswith('plan_'))
def handle_plan_selection(call):
    plan_code = call.data
    prices = {
        'plan_5': ("₹5", "40 Likes"),
        'plan_10': ("₹10", "90 Likes"),
        'plan_15': ("₹15", "145 Likes"),
        'plan_20': ("₹20", "205 Likes"),
        'plan_25': ("₹25", "270 Likes"),
        'plan_30': ("₹30", "340 Likes"),
        'plan_35': ("₹35", "415 Likes"),
        'plan_40': ("₹40", "500 Likes"),
        'plan_45': ("₹45", "585 Likes"),
        'plan_50': ("₹50", "700 Likes")
    }
    
    price, likes = prices.get(plan_code, ("₹5", "40 Likes"))
    user_states[call.from_user.id] = {'state': 'waiting_for_utr', 'plan': f"{price} - {likes}"}
    bot.answer_callback_query(call.id)

    payment_instruction = (
        f"✅ **Aapne select kiya:** `{price}` ➔ `{likes}`\n\n"
        "⚠️ **Zaroori Suraksha Suchna (Trust Notice):**\n"
        "Garena ke rules ke mutabiq, hum ek din mein ek limit (jaise 100 likes) hi provide kar sakte hain. Bachi hui likes aapko **agle din** milti rahengi. Isse aapki ID par **ban hone ka koi khatra nahi rahega** aur aapki ID 100% safe rahegi!\n\n"
        "💳 **Payment Details:**\n"
        "• **UPI ID:** `santoshkumarram085-1@oksbi`\n"
        "• **Name:** Santosh Rawat\n\n"
        "📝 **Aage kya karein?**\n"
        f"1. Upar di gayi UPI ID par exact **{price}** pay karein.\n"
        "2. Payment karne ke baad apna **12-digit UTR / Transaction Number** yahan chat mein bhej dein."
    )
    
    bot.send_message(call.message.chat.id, payment_instruction, parse_mode='Markdown')

# Handle text inputs (UTR and UID collection)
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
            "✅ **Payment Details Received Successfully!**\n\n"
            f"Plan: `{plan_selected}`\n"
            f"UTR: `{utr}`\n\n"
            "We have queued your UTR for verification. Your order is secure.\n\n"
            "🎯 Now, please send your **Game UID** where you want to receive your daily likes:",
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
            "🎉 **All Set! Your Order has been placed successfully!**\n\n"
            f"📦 Plan: `{plan_selected}`\n"
            f"🆔 UID: `{game_uid}`\n"
            f"🔢 UTR: `{utr}`\n\n"
            "Your payment is being verified by the admin. Garena rules ke mutabiq aapki daily likes delivery jald hi shuru ho jayegi! 🚀",
            parse_mode='Markdown',
            reply_markup=get_main_menu()
        )
    else:
        bot.reply_to(message, "Kripya neeche diye gaye menu ka use karein ya /start dabayein.", reply_markup=get_main_menu())

# Admin Command to view customer orders list
@bot.message_handler(commands=['list', 'export'])
def list_orders(message):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, username, plan_name, utr_number, game_uid, status FROM orders")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        bot.reply_to(message, "📂 No orders found in the database yet.", reply_markup=get_main_menu())
        return

    response = "📋 **Customer Orders List:**\n\n"
    for row in rows:
        response += f"🔹 **ID:** {row[0]}\n👤 **User:** @{row[2]} (ID: `{row[1]}`)\n📦 **Plan:** {row[3]}\n🔢 **UTR:** `{row[4]}`\n🆔 **UID:** `{row[5]}`\nStatus: {row[6]}\n----------------------------------\n"

    if len(response) > 4000:
        for x in range(0, len(response), 4000):
            bot.send_message(message.chat.id, response[x:x+4000], parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, response, parse_mode='Markdown', reply_markup=get_main_menu())

if __name__ == '__main__':
    print("Secure Bot is running...")
    bot.infinity_polling()
