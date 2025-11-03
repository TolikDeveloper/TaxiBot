from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "YOUR_BOT_TOKEN"
ADMIN_CHAT_ID = "-1003139491276"

# Bosqichlar
ASK_PHONE, ASK_ROUTE, ASK_NAME = range(3)


# --- /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("🚖 Taksi chaqirish"), KeyboardButton("📦 Pochta yuborish")]
    ]
    await update.message.reply_text(
        "Assalomu alaykum! Quyidagi xizmatlardan birini tanlang 👇",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# --- Taksi yoki pochta tanlanganda ---
async def choose_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["service"] = "taksi" if "Taksi" in text else "pochta"

    # Telefon so‘rash
    contact_button = KeyboardButton("📞 Telegram raqamimni yuborish", request_contact=True)
    reply_markup = ReplyKeyboardMarkup(
        [[contact_button]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await update.message.reply_text(
        "Iltimos, telefon raqamingizni yozing yoki pastdagi tugmani bosib yuboring 👇",
        reply_markup=reply_markup
    )
    return ASK_PHONE


# --- Raqamni tugma orqali olish ---
async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    context.user_data["phone"] = contact.phone_number
    await ask_route(update, context)
    return ASK_ROUTE


# --- Raqamni matn sifatida olish ---
async def phone_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await ask_route(update, context)
    return ASK_ROUTE


# --- Yo‘nalishni so‘rash ---
async def ask_route(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Toshkent → Turtkul", "Turtkul → Toshkent"]]
    await update.message.reply_text(
        "Yo‘nalishni tanlang 👇",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return ASK_NAME


# --- Ismni so‘rash ---
async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["route"] = update.message.text
    await update.message.reply_text("Ismingizni yozing (yoki ismingiz avtomatik olinadi):")
    return "SEND_ORDER"


# --- So‘rovni yuborish ---
async def send_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    name = update.message.text.strip() if update.message.text else user.first_name
    phone = context.user_data.get("phone")
    route = context.user_data.get("route")
    service = context.user_data.get("service")

    if service == "taksi":
        message = f"🚖 <b>Taksi buyurtmasi!</b>\n📍 Yo‘nalish: {route}\n🧍 Ism: {name}\n📞 Tel: {phone}"
    else:
        message = f"📢 <b>Pochta Hizmati!</b>\n📍 Yo‘nalish: {route}\n🧍 Ism: {name}\n📞 Tel: {phone}"

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message, parse_mode="HTML")

    # Foydalanuvchiga javob
    await update.message.reply_text("✅ So‘rovingiz yuborildi! Tez orada siz bilan bog‘lanishadi.")

    # Yana menyuni chiqarish
    keyboard = [
        [KeyboardButton("🚖 Taksi chaqirish"), KeyboardButton("📦 Pochta yuborish")]
    ]
    await update.message.reply_text(
        "Yana xizmat tanlash uchun pastdagi tugmalardan foydalaning 👇",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# --- Asosiy ishga tushirish ---
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("🚖 Taksi chaqirish|📦 Pochta yuborish"), choose_service))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    app.add_handler(MessageHandler(filters.Regex(r"^\+?\d{7,}$"), phone_text_handler))
    app.add_handler(MessageHandler(filters.Regex("Toshkent|Turtkul"), ask_name))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_order))

    app.run_polling()


if __name__ == "__main__":
    main()
