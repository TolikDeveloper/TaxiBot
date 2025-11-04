from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

# --- CONFIG (shu yerda yozamiz) ---
BOT_TOKEN = "8509764843:AAEOqn1Kaf8-n0OZXBizcGCLz_-OuYo7cO0"
GROUP_ID = "-1003139491276"  # Haydovchilar guruhi IDsi

# --- Conversation states ---
NAME, PHONE, DIRECTION, TIME, EXTRA, CONFIRM = range(6)

# --- Start komandasi ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("Buyurtma berish")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Assalomu alaykum! Buyurtma berish uchun 'Buyurtma berish' tugmasini bosing.", reply_markup=reply_markup)
    return NAME

# --- Ism ---
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Telefon raqamingizni kiriting (masalan: +998901234567)")
    return PHONE

# --- Telefon ---
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    
    keyboard = [["Turtkul Toshkent", "Toshkent Turtkul"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Qayerga borasiz?", reply_markup=reply_markup)
    return DIRECTION

# --- Yo‘nalish ---
async def get_direction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['direction'] = update.message.text
    
    keyboard = [["Hozir", "Soatini qo'lda yozing"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Qachon kerak?", reply_markup=reply_markup)
    return TIME

# --- Vaqt ---
async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['time'] = update.message.text
    await update.message.reply_text("Qo'shimcha ma'lumot (yo'lovchi soni, yuk) kiriting yoki bo'sh qoldiring:")
    return EXTRA

# --- Qo‘shimcha ma’lumot ---
async def get_extra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    extra = update.message.text
    context.user_data['extra'] = extra if extra else "Yo‘q"
    
    keyboard = [["Tasdiqlash"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    summary = f"Ism: {context.user_data['name']}\nTel: {context.user_data['phone']}\nYo‘nalish: {context.user_data['direction']}\nVaqt: {context.user_data['time']}\nQo'shimcha: {context.user_data['extra']}"
    await update.message.reply_text(f"Ma’lumotlarni tasdiqlaysizmi?\n\n{summary}", reply_markup=reply_markup)
    return CONFIRM

# --- Tasdiqlash va guruhga yuborish ---
async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    message = f"📢 Yangi buyurtma!\n📍 Yo‘nalish: {user_data['direction']}\n👥 Odamlar soni: {user_data['extra']}\n🧍 Ism: {user_data['name']}\n📞 Tel: {user_data['phone']}"
    
    # Guruhga yuborish
    await context.bot.send_message(chat_id=GROUP_ID, text=message)
    
    # Mijozga buyurtma tugmasini qaytarish
    keyboard = [[KeyboardButton("Buyurtma berish")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Buyurtmangiz qabul qilindi. Yana buyurtma berish uchun tugmani bosing.", reply_markup=reply_markup)
    
    return NAME

# --- Cancel ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Buyurtma bekor qilindi.")
    return ConversationHandler.END

# --- Main ---
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), MessageHandler(filters.Regex("Buyurtma berish"), start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            DIRECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_direction)],
            TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time)],
            EXTRA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_extra)],
            CONFIRM: [MessageHandler(filters.Regex("Tasdiqlash"), confirm_order)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
