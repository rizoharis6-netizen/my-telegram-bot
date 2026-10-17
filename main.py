from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import os

TOKEN = os.getenv("TOKEN")8890645496:AAG5bHCIQuCUyW7qHS0nkIXRm4upww_KbOk

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("O'zbekcha 🇺🇿", callback_data="lang_uz"),
         InlineKeyboardButton("Русский 🇷🇺", callback_data="lang_ru")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Assalomu alaykum! Tilni tanlang:\nЗдравствуйте! Выберите язык:",
        reply_markup=reply_markup
    )

# Tilni tanlash
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split("_")[1]
    context.user_data['lang'] = lang

    text = (
        "Quyidagi tugmani bosib telefon raqamingizni yuboring:"
        if lang == "uz" else
        "Нажмите кнопку ниже, чтобы отправить свой номер телефона:"
    )
    btn_text = "📞 Telefon raqamni yuborish" if lang == "uz" else "📞 Отправить номер телефона"
    
    reply_markup = ReplyKeyboardMarkup([[KeyboardButton(btn_text, request_contact=True)]], resize_keyboard=True, one_time_keyboard=True)
    await query.message.reply_text(text, reply_markup=reply_markup)

# Kontaktni qabul qilish
async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'uz')
    contact = update.message.contact
    context.user_data['phone'] = contact.phone_number

    text = (
        "Endi lokatsiyangizni yuboring (tugmani bosing):"
        if lang == "uz" else
        "Теперь отправьте свою локацию (нажмите кнопку):"
    )
    btn_text = "📍 Lokatsiyani yuborish" if lang == "uz" else "📍 Отправить локацию"

    reply_markup = ReplyKeyboardMarkup([[KeyboardButton(btn_text, request_location=True)]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(text, reply_markup=reply_markup)

# Lokatsiyani qabul qilish va menyuni ko'rsatish
async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'uz')
    location = update.message.location
    context.user_data['location'] = (location.latitude, location.longitude)

    keyboard = [
        [InlineKeyboardButton("🍿 Popcorn menyusi", callback_data="menu_categories")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "Lokatsiya qabul qilindi! Menyuni ko'rish uchun pastdagi tugmani bosing:"
        if lang == "uz" else
        "Локация принята! Нажмите кнопку ниже, чтобы посмотреть меню:"
    )
    await update.message.reply_text(text, reply_markup=reply_markup, reply_markup_remove=ReplyKeyboardRemove())

# Kategoriyalarni ko'rsatish
async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'uz')

    keyboard = [
        [InlineKeyboardButton("🍿 Klassik Popcorn", callback_data="cat_classic")],
        [InlineKeyboardButton("🍿 Karamel Popcorn", callback_data="cat_caramel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = "Kategoriyani tanlang:" if lang == "uz" else "Выберите категорию:"
    await query.message.edit_text(text, reply_markup=reply_markup)

# Kategoriya tanlanganda mahsulotni chiqarish
async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'uz')

    keyboard = [
        [InlineKeyboardButton("Sotib olish / Купить", callback_data="pay_card")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = "Popcorn narxi: 20 000 so'm" if lang == "uz" else "Цена попкорна: 20 000 сум"
    await query.message.edit_text(text, reply_markup=reply_markup)

# To'lov tanlovi va chek so'rash
async def payment_choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'uz')

    text = (
        "Iltimos, to'lov chekingizni rasm ko'rinishida yuboring:"
        if lang == "uz" else
        "Пожалуйста, отправьте чек об оплате в виде фото:"
    )
    await query.message.edit_text(text)

# Rasmni (chekni) qabul qilish va adminga yuborish
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'uz')
    user = update.effective_user
    photo = update.message.photo[-1].file_id

    ADMIN_ID = 123456789  # Bu yerga o'z admin ID raqamingizni yozasiz
    
    user_info = f"Buyurtmachi: {user.full_name} (@{user.username})\nID: {user.id}\nTel: {context.user_data.get('phone', 'Nomaʼlum')}"
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve_{user.id}_{lang}"),
            InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{user.id}_{lang}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Adminga yuborish
    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo,
        caption=f"Yangi chek keldi!\n\n{user_info}",
        reply_markup=reply_markup
    )

    user_reply = (
        "Rahmat! Chekingiz adminga yuborildi. Buyurtmangiz 6 soat ichida yetkazib beriladi!"
        if lang == "uz" else
        "Спасибо! Ваш чек отправлен админу. Ваш заказ будет доставлен в течение 6 часов!"
    )
    await update.message.reply_text(user_reply)

# Admin tasdiqlashi yoki rad etishi
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    action = parts[0]
    user_id = int(parts[1])
    user_lang = parts[2] if len(parts) > 2 else "uz"

    if action == "approve":
        msg = (
            "✅ Buyurtmangiz va to'lovingiz tasdiqlandi! Popcorn tayyorlanmoqda va 6 soat ichida yetkazib beriladi! 🍿"
            if user_lang == "uz" else
            "✅ Ваш заказ и оплата подтверждены! Попкорн готовится и будет доставлен в течение 6 часов! 🍿"
        )
        await context.bot.send_message(chat_id=user_id, text=msg)
        await query.edit_message_caption(caption=query.message.caption + "\n\n🟢 TASDIQLANDI / ПОДТВЕРЖДЕНО")

    elif action == "reject":
        msg = (
            "❌ To'lovingiz tasdiqlanmadi. Iltimos, chekni qaytadan tekshirib ko'ring yoki admin bilan bog'laning."
            if user_lang == "uz" else
            "❌ Ваша оплата не подтверждена. Пожалуйста, проверьте чек еще раз или свяжитесь с админом."
        )
        await context.bot.send_message(chat_id=user_id, text=msg)
        await query.edit_message_caption(caption=query.message.caption + "\n\n🔴 RAD ETILDI / ОТКЛОНЕНО")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(set_language, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(show_categories, pattern="^menu_categories$"))
    app.add_handler(CallbackQueryHandler(category_handler, pattern="^cat_"))
    app.add_handler(CallbackQueryHandler(payment_choice_handler, pattern="^pay_"))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^(approve|reject)_"))

    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    app.add_handler(MessageHandler(filters.LOCATION, location_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Popcorn Haris boti ishga tushdi...")
    app.run_polling()
