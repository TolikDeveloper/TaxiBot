from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from flask import Flask, request
import logging
import asyncio
import os
import config  # <-- bu fayldan token va id olinadi

# --- LOG sozlamalari ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# --- Bot ma’lumotlari ---
BOT_TOKEN = config.BOT_TOKEN
ADMIN_CHAT_ID = config.ADMIN_CHAT_ID
WEBHOOK_URL = config.WEBHOOK_URL

app_flask = Flask(__name__)

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

# --- Yakuniy qadam ---
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
        msg = f"📦 <b>Pochta xizmati!</b>\n📍 Yo‘nalish: {address}\n🧍 Ism: {name}\n📞 Tel: {phone}"

    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg, parse_mode="HTML")
        await update.message.reply_text("✅ So‘rovingiz yuborildi! Tez orada siz bilan bog‘lanishadi.")
    except Exception as e:
        logging.error(f"Guruhga yuborishda xatolik: {e}")
        await update.message.reply_text("❌ Xabar yuborishda xatolik yuz berdi, keyinroq urinib ko‘ring.")

    keyboard = [
        [KeyboardButton("🚖 Taksi chaqirish"), KeyboardButton("📦 Pochta yuborish")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Yana xizmat tanlash uchun tugmalardan foydalaning 👇", reply_markup=reply_markup)

# --- Telegram application ---
telegram_app = Application.builder().token(BOT_TOKEN).build()

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.Regex("🚖 Taksi chaqirish|📦 Pochta yuborish"), choose_service))
telegram_app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
telegram_app.add_handler(MessageHandler(filters.Regex(r"^\+?\d{7,}$"), phone_text_handler))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, location_handler))

# --- Flask webhook ---
@app_flask.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    asyncio.run(telegram_app.process_update(update))
    return "ok"

@app_flask.route("/", methods=["GET"])
def index():
    return "Bot ishlayapti 🚀"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    asyncio.run(telegram_app.bot.set_webhook(f"{WEBHOOK_URL}/{BOT_TOKEN}"))
    app_flask.run(host="0.0.0.0", port=port)
