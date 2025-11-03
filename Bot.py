from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = "8509764843:AAEOqn1Kaf8-n0OZXBizcGCLz_-OuYo7cO0"
ADMIN_CHAT_ID = -1003139491276

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
    return ASK_PHONE


# --- Tanlangan xizmat ---
async def choose_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "Taksi" in text:
        context.user_data["service"] = "taksi"
    elif "Pochta" in text:
        context.user_data["service"] = "pochta"
    else:
        await update.message.reply_text("Iltimos, menyudan xizmatni tanlang 👆")
        return ASK_PHONE

    # Telefon raqamini so‘rash tugmasi
    contact_button = KeyboardButton("📞 Telegram raqamimni yuborish", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text(
        "Iltimos, telefon raqamingizni yozing yoki pastdagi tugmani bosib yuboring 👇",
        reply_markup=reply_markup
    )
    return ASK_ROUTE


# --- Telefonni tugma orqali olish ---
async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    context.user_data["phone"] = contact.phone_number
    await update.message.reply_text("✅ Rahmat! Endi yo‘nalishni tanlang:")
    return ASK_NAME


# --- Telefonni matn orqali olish ---
async def phone_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    if not any(char.isdigit() for char in phone):
        await update.message.reply_text("❌ Iltimos, telefon raqamingizni to‘g‘ri yozing.")
        return ASK_ROUTE
    context.user_data["phone"] = phone
    await update.message.reply_text("✅ Rahmat! Endi yo‘nalishni tanlang:")
    return ASK_NAME


# --- Yo‘nalish ---
async def route_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text not in ["Toshkent → Turtkul", "Turtkul → Toshkent"]:
        await update.message.reply_text("❌ Iltimos, yo‘nalishni menyudan tanlang.")
        return ASK_NAME
    context.user_data["route"] = text
    await update.message.reply_text("Ismingizni kiriting (yoki avtomatik olinadi):")
    return ConversationHandler.END  # End conversation here, next message handled globally


# --- Yakuniy xabar yuborish ---
async def send_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    name = update.message.text.strip() if update.message.text else user.first_name
    phone = context.user_data.get("phone")
    route = context.user_data.get("route")
    service = context.user_data.get("service")

    if not all([phone, route, service]):
        await update.message.reply_text("❌ Iltimos, avval barcha ma'lumotlarni to‘ldiring.")
        return

    if service == "taksi":
        message = f"🚖 <b>Taksi buyurtmasi!</b>\n📍 Yo‘nalish: {route}\n🧍 Ism: {name}\n📞 Tel: {phone}"
    else:
        message = f"📢 <b>Pochta Hizmati!</b>\n📍 Yo‘nalish: {route}\n🧍 Ism: {name}\n📞 Tel: {phone}"

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message, parse_mode="HTML")

    # Javob + yana menyuni chiqarish
    keyboard = [
        [KeyboardButton("🚖 Taksi chaqirish"), KeyboardButton("📦 Pochta yuborish")]
    ]
    await update.message.reply_text(
        "✅ So‘rovingiz yuborildi! Tez orada siz bilan bog‘lanishadi.\n\nYana xizmat tanlash uchun pastdagi tugmalardan foydalaning 👇",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# --- Asosiy ishga tushirish ---
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start),
                      MessageHandler(filters.Regex("🚖 Taksi chaqirish|📦 Pochta yuborish"), choose_service)],
        states={
            ASK_PHONE: [
                MessageHandler(filters.CONTACT, contact_handler),
                MessageHandler(filters.TEXT & ~filters.COMMAND, phone_text_handler)
            ],
            ASK_NAME: [MessageHandler(filters.Regex("Toshkent → Turtkul|Turtkul → Toshkent"), route_handler)],
        },
        fallbacks=[]
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_order))

    app.run_polling()


if __name__ == "__main__":
    main()

