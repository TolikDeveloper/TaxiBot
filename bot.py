from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 1️⃣ Bot tokenini shu yerga joylashtirasan
BOT_TOKEN = "8509764843:AAEOqn1Kaf8-n0OZXBizcGCLz_-OuYo7cO0"

# 2️⃣ Guruh chat ID (masalan: -1001234567890)
GROUP_CHAT_ID = -1003139491276  # O'zingning guruh ID sini yoz

# 3️⃣ Buyurtma kelganida chaqiriladigan funksiya
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Ma'lumotlarni ajratish (soddaroq usul)
    lines = text.split("\n")
    if len(lines) >= 4:
        manzil = lines[0].replace("Turtkul → Toshkent", "🏢Turtkul → Toshkent")
        odam_soni = lines[1].replace("3 kishi", "📝3 kishi")
        ism = lines[2].replace("Ism:", "📌Ism:")
        tel = lines[3].replace("Tel:", "📞Tel:")

        # Yuboriladigan matn
        msg = f"📢 Yangi buyurtma\n{manzil}\n{odam_soni}\n{ism}\n{tel}"

        # Guruhga yuborish
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)

        # Tasdiq sifatida foydalanuvchiga ham yuborish
        await update.message.reply_text("✅ Buyurtma qabul qilindi va guruhga yuborildi.")
    else:
        await update.message.reply_text("❌ Ma'lumot to‘liq emas. Iltimos, to‘liq shaklda yuboring.")

# 4️⃣ Botni ishga tushirish
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
