from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8509764843:AAEOqn1Kaf8-n0OZXBizcGCLz_-OuYo7cO0"
ADMIN_CHAT_ID = "-1003139491276"


# --- /start komandasi ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    first_name = user.first_name or "Ismsiz foydalanuvchi"

    # Tugmalar: raqam yuborish yoki o‘zi yozish
    contact_button = KeyboardButton("📞 Telegram raqamimni yuborish", request_contact=True)
    reply_markup = ReplyKeyboardMarkup(
        [[contact_button]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        f"Salom, {first_name}! 🚖\nTaksi chaqirish uchun telefon raqamingizni yozing "
        f"yoki pastdagi tugmani bosib raqamingizni yuboring 👇",
        reply_markup=reply_markup
    )


# --- Agar foydalanuvchi raqamni tugma orqali yuborsa ---
async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    phone = contact.phone_number
    name = update.message.from_user.first_name or "Ismsiz foydalanuvchi"

    context.user_data["phone"] = phone
    context.user_data["name"] = name

    await update.message.reply_text("✅ Rahmat! Endi manzilingizni yuboring (masalan: Chilonzor, 12-daha).")


# --- Agar foydalanuvchi raqamni yozib yuborsa ---
async def phone_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    name = update.message.from_user.first_name or "Ismsiz foydalanuvchi"

    # Oddiy tekshirish: raqamda faqat raqamlar yoki + belgisi bo‘lsin
    if not any(char.isdigit() for char in phone):
        await update.message.reply_text("❌ Iltimos, telefon raqamingizni to‘g‘ri yozing.")
        return

    context.user_data["phone"] = phone
    context.user_data["name"] = name

    await update.message.reply_text("✅ Rahmat! Endi manzilingizni yuboring (masalan: Chilonzor, 12-daha).")


# --- Manzilni qabul qilish va guruhga yuborish ---
async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    address = update.message.text
    phone = context.user_data.get("phone")
    name = context.user_data.get("name")

    if not phone:
        await update.message.reply_text("Iltimos, avval telefon raqamingizni yuboring.")
        return

    msg = f"🚖 <b>Yangi taksi so‘rovi!</b>\n👤 {name}\n📞 {phone}\n📍 Manzil: {address}"
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg, parse_mode="HTML")

    # Mijozga javob
    await update.message.reply_text("✅ So‘rovingiz yuborildi! Taksi tez orada siz bilan bog‘lanadi.")

    # Yana “Taksi chaqirish” menyusini chiqazish
    contact_button = KeyboardButton("🚖 Taksi chaqirish", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True)
    await update.message.reply_text("Yana taksi chaqirishni xohlaysizmi?", reply_markup=reply_markup)


# --- Asosiy ishga tushirish ---
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    app.add_handler(MessageHandler(filters.Regex(r"^\+?\d{7,}$"), phone_text_handler))  # raqam yozilsa
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, location_handler))

    app.run_polling()


if __name__ == "__main__":
    main()
