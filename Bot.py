from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import os

BOT_TOKEN = os.getenv("8509764843:AAEOqn1Kaf8-n0OZXBizcGCLz_-OuYo7cO0")
ADMIN_CHAT_ID = os.getenv("-1003139491276")

# Bosqichlar
ASK_NAME, ASK_PHONE, ASK_ROUTE, ASK_PEOPLE = range(4)

# 🚖 Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("🚖 Taksi chaqirish")]]
    await update.message.reply_text(
        "Assalomu alaykum! Taksi buyurtma berish uchun pastdagi tugmani bosing 👇",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# 🚕 Taksi chaqirish jarayoni boshlanishi
async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ismingizni kiriting:")
    return ASK_NAME

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Telefon raqamingizni kiriting (masalan: +998901234567):")
    return ASK_PHONE

async def ask_route(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    keyboard = [["Turtkul → Toshkent", "Toshkent → Turtkul"]]
    await update.message.reply_text(
        "Qayerdan qayerga ketmoqchisiz?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return ASK_ROUTE

async def ask_people(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["route"] = update.message.text
    await update.message.reply_text("Nechta kishi borasiz?")
    return ASK_PEOPLE

# ✅ Hammasi tayyor bo‘lganda
async def send_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["people"] = update.message.text

    name = context.user_data["name"]
    phone = context.user_data["phone"]
    route = context.user_data["route"]
    people = context.user_data["people"]

    message = f"📢 Yangi buyurtma\n🏢{route}\n📝{people} kishi\n📌Ism: {name}\n📞Tel: {phone}"

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message)

    # Foydalanuvchiga javob
    keyboard = [[KeyboardButton("🚖 Taksi chaqirish")]]
    await update.message.reply_text(
        "✅ Buyurtma yuborildi! Tez orada siz bilan bog‘lanishadi.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

    return ConversationHandler.END

# Bekor qilish
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Xizmat uchun rahmat 😊")
    keyboard = [[KeyboardButton("🚖 Taksi chaqirish")]]
    await update.message.reply_text(
        "Yana buyurtma berish uchun pastdagi tugmani bosing 👇",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return ConversationHandler.END

# Asosiy qism
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
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    app.run_polling()

if __name__ == "__main__":
    main()
