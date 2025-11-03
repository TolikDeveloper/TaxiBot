from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# 🚀 To‘g‘ridan-to‘g‘ri token va guruh ID
BOT_TOKEN = "8509764843:AAEOqn1Kaf8-n0OZXBizcGCLz_-OuYo7cO0"
ADMIN_CHAT_ID = "-1003139491276

# Bosqichlar
ASK_NAME, ASK_PHONE, ASK_ROUTE, ASK_PEOPLE = range(4)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("🚖 Taksi chaqirish")]]
    await update.message.reply_text(
        "Assalomu alaykum! Taksi buyurtma berish uchun pastdagi tugmani bosing 👇",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# Ismni so‘rash
async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ismingizni kiriting:")
    return ASK_NAME

# Telefon raqamini so‘rash
async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text("Telefon raqamingizni kiriting (masalan: +998901234567):")
    return ASK_PHONE

# Yo‘nalishni so‘rash
async def ask_route(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text.strip()
    keyboard = [["Turtkul → Toshkent", "Toshkent → Turtkul"]]
    await update.message.reply_text(
        "Qayerdan qayerga ketmoqchisiz?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return ASK_ROUTE

# Odamlar sonini so‘rash
async def ask_people(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["route"] = update.message.text.strip()
    await update.message.reply_text("Nechta kishi borasiz?")
    return ASK_PEOPLE

# ✅ Buyurtma yuborish
async def send_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["people"] = update.message.text.strip()

    name = context.user_data.get("name")
    phone = context.user_data.get("phone")
    route = context.user_data.get("route")
    people = context.user_data.get("people")

    message = (
        f"📢 *Yangi buyurtma!*\n"
        f"📍 Yo‘nalish: {route}\n"
        f"👥 Odamlar soni: {people}\n"
        f"🧍 Ism: {name}\n"
        f"📞 Tel: {phone}"
    )

    # Admin guruhiga yuborish
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message, parse_mode="Markdown")

    # Foydalanuvchiga javob
    keyboard = [[KeyboardButton("🚖 Taksi chaqirish")]]
    await update.message.reply_text(
        "✅ Buyurtma yuborildi! Tez orada siz bilan bog‘lanishadi.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

    return ConversationHandler.END

# ❌ Bekor qilish
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Xizmat uchun rahmat 😊")
    keyboard = [[KeyboardButton("🚖 Taksi chaqirish")]]
    await update.message.reply_text(
        "Yana buyurtma berish uchun pastdagi tugmani bosing 👇",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return ConversationHandler.END

# Asosiy funksiya
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("🚖 Taksi chaqirish"), ask_name)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_route)],
            ASK_ROUTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_people)],
            ASK_PEOPLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_order)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    print("🚀 Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
