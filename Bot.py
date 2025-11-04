from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import logging

# --- LOG sozlamalari ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# --- Bot ma’lumotlari ---
BOT_TOKEN = "8509764843:AAEOqn1Kaf8-n0OZXBizcGCLz_-OuYo7cO0"
ADMIN_CHAT_ID = "-1003139491276"

# --- /start komandasi ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    first_name = user.first_name or "Ismsiz foydalanuvchi"

    keyboard = [
        [KeyboardButton("🚖 Taksi chaqirish"), KeyboardButton("📦 Pochta yuborish")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"Salom, {first_name}! Quyidagi xizmatlardan birini tanlang 👇",
        reply_markup=reply_markup,
    )


# --- Xizmat tanlash ---
async def choose_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "Taksi" in text:
        context.user_data["service"] = "taksi"
        msg_text = "Taksi chaqirish uchun telefon raqamingizni yozing yoki pastdagi tugmani bosing 👇"
    elif "Pochta" in text:
        context.user_data["service"] = "pochta"
        msg_text = "Pochta yuborish uchun telefon raqamingizni yozing yoki pastdagi tugmani bosing 👇"
    else:
        await update.message.reply_text("Iltimos, menyudan xizmatni tanlang 👆")
        return

    contact_button = KeyboardButton("📞 Telegram raqamimni yuborish", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True)
    await update.message.reply_text(msg_text, reply_markup=reply_markup)


# --- Kontakt yuborilganda ---
async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    phone = contact.phone_number
    name = update.message.from_user.first_name or "Ismsiz foydalanuvchi"

    context.user_data["phone"] = phone
    context.user_data["name"] = name

    await update.message.reply_text("✅ Rahmat! Endi yo‘nalishni yozing (masalan: Toshkent → Turtkul).")


# --- Telefon raqamni qo‘lda yozganda ---
async def phone_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    name = update.message.from_user.first_name or "Ismsiz foydalanuvchi"

    if not any(char.isdigit() for char in phone):
        await update.message.reply_text("❌ Iltimos, telefon raqamingizni to‘g‘ri yozing.")
        return

    context.user_data["phone"] = phone
    context.user_data["name"] = name

    await update.message.reply_text("✅ Rahmat! Endi yo‘nalishni yozing (masalan: Toshkent → Turtkul).")


# --- Yakuniy qadam: xabarni guruhga yuborish ---
async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    address = update.message.text.strip()
    phone = context.user_data.get("phone")
    name = context.user_data.get("name")
    service = context.user_data.get("service")

    if not all([phone, service]):
        await update.message.reply_text("Iltimos, avval telefon raqamingizni yuboring va xizmatni tanlang.")
        return

    if service == "taksi":
        msg = f"🚖 <b>Yangi taksi buyurtmasi!</b>\n📍 Yo‘nalish: {address}\n🧍 Ism: {name}\n📞 Tel: {phone}"
    else:
        msg = f"📢 <b>Pochta Hizmati!</b>\n📍 Yo‘nalish: {address}\n🧍 Ism: {name}\n📞 Tel: {phone}"

    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg, parse_mode="HTML")
        await update.message.reply_text("✅ So‘rovingiz yuborildi! Tez orada siz bilan bog‘lanishadi.")
    except Exception as e:
        logging.error(f"Guruhga yuborishda xatolik: {e}")
        await update.message.reply_text("❌ Xabar yuborishda xatolik yuz berdi, keyinroq urinib ko‘ring.")

    # Yana menyuni qaytarish
    keyboard = [
        [KeyboardButton("🚖 Taksi chaqirish"), KeyboardButton("📦 Pochta yuborish")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Yana xizmat tanlash uchun tugmalardan foydalaning 👇", reply_markup=reply_markup)


# --- Asosiy ---
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("🚖 Taksi chaqirish|📦 Pochta yuborish"), choose_service))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    app.add_handler(MessageHandler(filters.Regex(r"^\+?\d{7,}$"), phone_text_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, location_handler))

    print("Bot ishga tushdi 🚀")
    app.run_polling()


if __name__ == "__main__":
    main()
