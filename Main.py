# bot.py (barcha kod shu yerga joylashtiriladi)
import re
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler, ConversationHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIG: bu joyga o'zingizning token va guruh chat id-ni qo'ying ---
BOT_TOKEN = "8509764843:AAEOqn1Kaf8-n0OZXBizcGCLz_-OuYo7cO0"         # <-- BU YERNI O'ZGARTIRING
ADMIN_GROUP_CHAT_ID = -1003139491276      # <-- BU YERNI O'ZGARTIRING (misol -100...)

# --- Konversatsiya bosqichlari ---
(NAME, CONFIRM_NAME, PHONE_CHOICE, GET_PHONE, ROUTE, PASSENGERS, CONFIRM) = range(7)

phone_regex = re.compile(r'^\+998\d{9}$')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    tg_name = user.first_name or ""
    context.user_data['tg_name'] = tg_name
    keyboard = [
        [InlineKeyboardButton("Telegramdagi ismni ishlatish: " + tg_name, callback_data="use_tg_name")],
        [InlineKeyboardButton("Yangi ism kiritish", callback_data="new_name")]
    ]
    # agar /start komandasi guruhda bo'lsa, update.message bo'lmasligi mumkin; shuning uchun tekshiring
    if update.message:
        await update.message.reply_text("Salom! Ismingizni qanday olishni xohlaysiz?", reply_markup=InlineKeyboardMarkup(keyboard))
    return NAME

async def name_choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "use_tg_name":
        context.user_data['name'] = context.user_data.get('tg_name', "")
        await q.message.reply_text(f"Ismingiz: {context.user_data['name']}")
        return await ask_phone(q.message, context)
    else:
        await q.message.reply_text("Iltimos, ismingizni yozing:")
        return CONFIRM_NAME

async def confirm_name_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    context.user_data['name'] = name
    await update.message.reply_text(f"Siz kiritdingiz: {name}")
    return await ask_phone(update.message, context)

async def ask_phone(msg, context):
    kb = ReplyKeyboardMarkup([
        [KeyboardButton("Kontaktni ulash", request_contact=True)],
        ["Qo'l bilan kiriting (+998911234567)"]
    ], resize_keyboard=True, one_time_keyboard=True)
    await msg.reply_text("Telefon raqamingizni yuboring. Telegram kontaktni ulash yoki qo'l bilan kiritishingiz mumkin.", reply_markup=kb)
    return PHONE_CHOICE

async def phone_choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        phone = update.message.contact.phone_number
        if not phone.startswith("+"):
            if phone.startswith("998") and len(phone) == 12:
                phone = "+" + phone
        context.user_data['phone'] = phone
        await update.message.reply_text(f"Telef: {phone} qabul qilindi.")
        return await ask_route(update, context)
    else:
        text = update.message.text.strip()
        if text.startswith("Qo'l bilan") or text.startswith("+"):
            await update.message.reply_text("Iltimos telefonni +998… formatida yozib yuboring (masalan +998911234567):")
            return GET_PHONE
        else:
            await update.message.reply_text("Telefon yuboring (kontakt yoki +998... formatida):")
            return PHONE_CHOICE

async def get_phone_manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    if phone_regex.match(phone):
        context.user_data['phone'] = phone
        await update.message.reply_text(f"Telefon qabul qilindi: {phone}")
        return await ask_route(update, context)
    else:
        await update.message.reply_text("Telefon formati noto‘g‘ri. Iltimos +998911234567 ko'rinishida kiriting.")
        return GET_PHONE

async def ask_route(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Turtkul → Toshkent", callback_data="T2T")],
        [InlineKeyboardButton("Toshkent → Turtkul", callback_data="T2K")]
    ])
    await update.message.reply_text("Qaysi yo‘nalish?", reply_markup=kb)
    return ROUTE

async def route_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    route = "Turtkul → Toshkent" if q.data == "T2T" else "Toshkent → Turtkul"
    context.user_data['route'] = route
    await q.message.reply_text(f"Yo‘nalish: {route}\nNechta odam bor? (raqam bilan yozing)")
    return PASSENGERS

async def passengers_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("Iltimos faqat raqam kiriting (masalan: 2).")
        return PASSENGERS
    context.user_data['passengers'] = int(text)
    name = context.user_data.get('name')
    phone = context.user_data.get('phone')
    route = context.user_data.get('route')
    pax = context.user_data.get('passengers')
    summary = f"✅ Yangi buyurtma:\n{route}\n{pax} kishi\nIsm: {name}\nTel: {phone}\n\nTasdiqlaysizmi?"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Tasdiqlash va yuborish", callback_data="confirm_send")],
        [InlineKeyboardButton("Bekor qilish", callback_data="cancel")]
    ])
    await update.message.reply_text(summary, reply_markup=kb)
    return CONFIRM

async def confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "confirm_send":
        name = context.user_data.get('name')
        phone = context.user_data.get('phone')
        route = context.user_data.get('route')
        pax = context.user_data.get('passengers')
        msg = f"📢 <b>Yangi buyurtma</b>\n{route}\n{pax} kishi\nIsm: {name}\nTel: {phone}"
        try:
            await context.bot.send_message(chat_id=ADMIN_GROUP_CHAT_ID, text=msg, parse_mode="HTML")
            await q.message.reply_text("Sizning xabaringiz admin guruhiga yuborildi. Rahmat!")
        except Exception as e:
            await q.message.reply_text("Guruhga yuborishda xatolik yuz berdi. Admin bilan bog'laning.")
            logger.exception(e)
    else:
        await q.message.reply_text("Bekor qilindi.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bekor qilindi.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [CallbackQueryHandler(name_choice_handler)],
            CONFIRM_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_name_received)],
            PHONE_CHOICE: [MessageHandler(filters.CONTACT, phone_choice_handler),
                           MessageHandler(filters.TEXT & ~filters.COMMAND, phone_choice_handler)],
            GET_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone_manual)],
            ROUTE: [CallbackQueryHandler(route_handler)],
            PASSENGERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, passengers_handler)],
            CONFIRM: [CallbackQueryHandler(confirm_handler)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(conv_handler)

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == '__main__':
    main()
