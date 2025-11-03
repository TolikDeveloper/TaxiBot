from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

# --- Bosqichlar ---
ASK_NAME, ASK_PHONE, ASK_ROUTE, ASK_PEOPLE = range(4)

# --- Token va guruh ID ---
BOT_TOKEN = "8509764843:AAEOqn1Kaf8-n0OZXBizcGCLz_-OuYo7cO0"  # o'zingning bot tokenini yoz
GROUP_CHAT_ID = -1003139491276  # o'zingning guruh ID sini yoz


# 🚀 /start buyrug'i
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["🚖 Taksi chaqirish"]]
    await update.message.reply_text(
        "Salom 👋\nXush kelibsiz!\nQuyidagi tugma orqali taksi chaqirishingiz mumkin:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    )


# 🚖 Taksi chaqirish bosilganda
async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📌 Ismingizni kiriting:")
    return ASK_NAME


# 📋 Ismni olish
async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("📞 Telefon raqamingizni kiriting (+998 bilan):")
    return ASK_PHONE


# ☎️ Telefon raqamini olish
async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    if not phone.startswith("+998") or len(phone) < 9:
        await update.message.reply_text("❌ Raqam noto‘g‘ri. Namuna: +998901234567")
        return ASK_PHONE

    context.user_data["phone"] = phone
    reply_keyboard = [["Turtkul → Toshkent", "Toshkent → Turtkul"]]
    await update.message.reply_text(
        "🏙 Qayerdan qayerga borasiz?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return ASK_ROUTE


# 🚗 Yo‘nalishni olish
async def ask_route(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["route"] = update.message.text
    await update.message.reply_text("👥 Nechta kishi borasiz?")
    return ASK_PEOPLE


# 👥 Odam sonini olish va yakuniy xabar
async def ask_people(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["people"] = update.message.text

    name = context.user_data["name"]
    phone = context.user_data["phone"]
    route = context.user_data["route"]
    people = context.user_data["people"]

    msg = (
        f"📢 Yangi buyurtma\n"
        f"🏢{route}\n"
        f"📝{people} kishi\n"
        f"📌Ism: {name}\n"
        f"📞Tel: {phone}"
    )

    # Guruhga yuborish
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)

    # Foydalanuvchiga javob
    reply_keyboard = [["🚖 Taksi chaqirish"]]
    await update.message.reply_text(
        "✅ Buyurtma qabul qilindi va guruhga yuborildi.\n"
        "Yana taksi kerak bo‘lsa, pastdagi tugmani bosing 🚕",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    )

    return ConversationHandler.END


# ❌ Bekor qilish
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["🚖 Taksi chaqirish"]]
    await update.message.reply_text(
        "❌ Jarayon bekor qilindi.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    )
    return ConversationHandler.END


# 🔧 Botni ishga tushirish
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^(🚖 Taksi chaqirish)$"), start_order),
            CommandHandler("start", start),
        ],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            ASK_ROUTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_route)],
            ASK_PEOPLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_people)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("start", start))
    app.run_polling()


if __name__ == "__main__":
    main()
