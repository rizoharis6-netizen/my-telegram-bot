from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Token va Admin ID
TOKEN = "8890645496:AAG5bHCIQuCUyW7qHS0nkIXRm4upww_KbOk"  # BotFather bergan tokenni shu yerga yozing
ADMIN_ID = 8515986873                   # Sizning ID raqamingiz
KARTA_NUM = "5614 6820 2437 0274 (RAHMANOVA J)"  # Karta raqamingiz

# /start komandasi - BIRINCHI BO'LIB TIL SO'RALADI
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "✨ **Popcorn Haris** botiga xush kelibsiz!\n"
        "Iltimos, tilni tanlang / Пожалуйста, выберите язык:"
    )
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

# Til tanlangandan so'ng Asosiy Menyu
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = "uz" if query.data == "lang_uz" else "ru"
    context.user_data['lang'] = lang

    if lang == "uz":
        btn_text = "🍿 Popcornga buyurtma berish"
        msg_text = "✨ **Popcorn Haris** rasmiy botiga xush kelibsiz! 🍿\n\nBuyurtma berish uchun quyidagi tugmani bosing:"
    else:
        btn_text = "🍿 Заказать попкорн"
        msg_text = "✨ Добро пожаловать в официальный бот **Popcorn Haris**! 🍿\n\nНажмите кнопку ниже, чтобы сделать заказ:"

    keyboard = [[InlineKeyboardButton(btn_text, callback_data="menu_categories")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(msg_text, reply_markup=reply_markup, parse_mode="Markdown")

# Popcorn turlari va narxlari
async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get('lang', 'uz')

    if lang == "uz":
        keyboard = [
            [InlineKeyboardButton("🇺🇸 Amerikanskiy (15,000 so'm)", callback_data="cat_american")],
            [InlineKeyboardButton("🍿 Popcorn 1L (8,000 so'm)", callback_data="cat_container_1l")],
            [InlineKeyboardButton("🍿 Popcorn 1.5L (10,000 so'm)", callback_data="cat_container_1.5l")],
            [InlineKeyboardButton("📦 Paketchalik 100gr (5,000 so'm)", callback_data="cat_packet")]
        ]
        text = (
            "👇 **Popcorn turlari va narxlari:**\n"
            "*(Diqqat: 10 tadan yuqori buyurtmalar uchun maxsus shartlar amal qiladi!)*\n\n"
            "Marhamat, turini tanlang:"
        )
    else:
        keyboard = [
            [InlineKeyboardButton("🇺🇸 Американский (15,000 сум)", callback_data="cat_american")],
            [InlineKeyboardButton("🍿 Попкорн 1L (8,000 сум)", callback_data="cat_container_1l")],
            [InlineKeyboardButton("🍿 Попкорн 1.5L (10,000 сум)", callback_data="cat_container_1.5l")],
            [InlineKeyboardButton("📦 В пакете 100gr (5,000 сум)", callback_data="cat_packet")]
        ]
        text = (
            "👇 **Виды попкорна и цены:**\n"
            "*(Внимание: Для заказов более 10 штук действуют специальные условия!)*\n\n"
            "Пожалуйста, выберите вид:"
        )

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

# Kategoriya tanlanganda
async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get('lang', 'uz')
    data = query.data

    cat_names = {
        "uz": {
            "cat_american": "🇺🇸 Amerikanskiy popcorn (15 000 so'm)",
            "cat_container_1l": "🍿 Popcorn 1L (8 000 so'm)",
            "cat_container_1.5l": "🍿 Popcorn 1.5L (10 000 so'm)",
            "cat_packet": "📦 Paketchalik 100gr (5 000 so'm)"
        },
        "ru": {
            "cat_american": "🇺🇸 Американский попкорн (15 000 сум)",
            "cat_container_1l": "🍿 Попкорн 1L (8 000 сум)",
            "cat_container_1.5l": "🍿 Попкорн 1.5L (10 000 сум)",
            "cat_packet": "📦 В пакете 100gr (5 000 сум)"
        }
    }

    selected_category = cat_names[lang].get(data, "Popcorn")
    context.user_data['popcorn_type'] = selected_category
    context.user_data['waiting_for_quantity'] = True

    if lang == "uz":
        msg = f"Siz tanladingiz: **{selected_category}** ✅\n\nNechta dona buyurtma bermoqchisiz? (Miqdorni raqam bilan yozing, masalan: `1` yoki `12`):"
    else:
        msg = f"Вы выбрали: **{selected_category}** ✅\n\nСколько штук хотите заказать? (Введите количество цифрой, например: `1` или `12`):"

    await query.message.edit_text(msg, parse_mode="Markdown")

# Miqdorni qabul qilish va telefon raqam so'rash
async def quantity_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('waiting_for_quantity'):
        return

    lang = context.user_data.get('lang', 'uz')
    text = update.message.text

    try:
        quantity = int(text)
    except ValueError:
        err_msg = "Iltimos, faqat raqam kiriting (masalan: 5 yoki 12):" if lang == "uz" else "Пожалуйста, введите только цифры (например: 5 или 12):"
        await update.message.reply_text(err_msg)
        return

    context.user_data['quantity'] = quantity
    context.user_data['waiting_for_quantity'] = False

    if quantity >= 10:
        bulk_msg = (
            f"🎁 Siz 10 tadan ko'p ({quantity} ta) buyurtma berdingiz! Bu ulgurji buyurtma sifatida qabul qilindi."
            if lang == "uz" else
            f"🎁 Вы заказали более 10 штук ({quantity} шт)! Заказ принят как оптовый."
        )
        await update.message.reply_text(bulk_msg)

    if lang == "uz":
        btn_text = "📞 Telefon raqamni ulashish"
        msg = f"Miqdor: **{quantity} ta** ✅\n\nBiz bilan bog'lanish uchun **'📞 Telefon raqamni ulashish'** tugmasini bosing:"
    else:
        btn_text = "📞 Поделиться номером телефона"
        msg = f"Количество: **{quantity} шт** ✅\n\nНажмите кнопку **'📞 Поделиться номером телефона'**:"

    contact_keyboard = [[KeyboardButton(btn_text, request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(contact_keyboard, resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode="Markdown")

# Telefon raqamni qabul qilish va lokatsiya so'rash
async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'uz')
    contact = update.message.contact
    context.user_data['phone'] = contact.phone_number

    if lang == "uz":
        btn_text = "📍 Lokatsiyani ulashish"
        msg = "Raqamingiz qabul qilindi! 📱\n\nYetkazib berishimiz uchun **'📍 Lokatsiyani ulashish'** tugmasini bosing:"
    else:
        btn_text = "📍 Поделиться геолокацией"
        msg = "Ваш номер принят! 📱\n\nДля доставки нажмите кнопку **'📍 Поделиться геолокацией'**:"

    location_keyboard = [[KeyboardButton(btn_text, request_location=True)]]
    reply_markup = ReplyKeyboardMarkup(location_keyboard, resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode="Markdown")

# Lokatsiyani qabul qilish va to'lov turini tanlatish
async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'uz')
    location = update.message.location
    context.user_data['location'] = (location.latitude, location.longitude)

    if lang == "uz":
        keyboard = [
            [InlineKeyboardButton("💳 Karta orqali (Online to'lov)", callback_data="pay_card")],
            [InlineKeyboardButton("💵 Maxsulot borgach naqd ko'rinishida", callback_data="pay_cash")],
            [InlineKeyboardButton("🤝 Mahsulot sotilgach pulini berish", callback_data="pay_after_sale")]
        ]
        loc_msg = "Lokatsiyangiz qabul qilindi! 📍"
        pay_msg = "Qaysi usulda to'lamoqchisiz?"
    else:
        keyboard = [
            [InlineKeyboardButton("💳 Карта (Онлайн оплата)", callback_data="pay_card")],
            [InlineKeyboardButton("💵 Наличными при получении", callback_data="pay_cash")],
            [InlineKeyboardButton("🤝 Оплата после реализации товара", callback_data="pay_after_sale")]
        ]
        loc_msg = "Ваша геолокация принята! 📍"
        pay_msg = "Каким способом хотите оплатить?"

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(loc_msg, reply_markup=ReplyKeyboardRemove())
    await update.message.reply_text(pay_msg, reply_markup=reply_markup)

# To'lov turini tanlash
async def payment_choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get('lang', 'uz')
    data = query.data
    user = update.effective_user
    p_type = context.user_data.get('popcorn_type', 'Nomaʼlum')
    quantity = context.user_data.get('quantity', 1)
    phone = context.user_data.get('phone', 'Nomaʼlum')
    lat, lon = context.user_data.get('location', (0, 0))

    if data == "pay_card":
        context.user_data['pay_method'] = "Karta orqali"
        if lang == "uz":
            card_msg = f"💳 **Karta orqali to'lov:**\n\nKarta raqami: `{KARTA_NUM}`\n\nTo'lovni amalga oshirgach, **chek skrinshotini (rasmini)** shu botga yuboring!"
        else:
            card_msg = f"💳 **Оплата картой:**\n\nНомер карты: `{KARTA_NUM}`\n\nПосле оплаты отправьте **скриншот чека** в этот бот!"

        await query.message.edit_text(card_msg, parse_mode="Markdown")

    else:
        pay_type_name = "Maxsulot borgach naqd ko'rinishida" if data == "pay_cash" else "Mahsulot sotilgach pulini berish"
        context.user_data['pay_method'] = pay_type_name

        # Adminga buyurtma bildirishnomasi
        admin_text = (
            f"🚨 **YANGI BUYURTMA!** 🍿\n\n"
            f"👤 Mijoz: {user.full_name} (@{user.username})\n"
            f"📞 Tel: {phone}\n"
            f"🍿 Turi: {p_type}\n"
            f"📦 Soni: {quantity} ta\n"
            f"🌐 Til: {lang.upper()}\n"
            f"💵 To'lov turi: {pay_type_name}"
        )

        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown")
        await context.bot.send_location(chat_id=ADMIN_ID, latitude=lat, longitude=lon)

        confirm_msg = (
            "✅ Buyurtmangiz qabul qilindi! 6 soat ichida yetkazib beriladi! 🍿"
            if lang == "uz" else
            "✅ Ваш заказ принят! Будет доставлен в течение 6 часов! 🍿"
        )
        await query.message.edit_text(confirm_msg)

# Chek (rasm) yuborilganda
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'uz')
    user = update.effective_user
    photo_file_id = update.message.photo[-1].file_id

    p_type = context.user_data.get('popcorn_type', 'Popcorn')
    quantity = context.user_data.get('quantity', 1)
    phone = context.user_data.get('phone', 'Nomaʼlum')
    lat, lon = context.user_data.get('location', (0, 0))

    keyboard = [
        [
            InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve_{user.id}_{lang}"),
            InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{user.id}_{lang}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    caption = (
        f"📥 **Yangi to'lov cheki (Karta orqali)!** 🍿\n\n"
        f"👤 Mijoz: {user.full_name} (@{user.username})\n"
        f"📞 Tel: {phone}\n"
        f"🍿 Turi: {p_type}\n"
        f"📦 Soni: {quantity} ta\n"
        f"🌐 Til: {lang.upper()}\n"
        f"ID: `{user.id}`"
    )

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo_file_id,
        caption=caption,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    if lat != 0:
        await context.bot.send_location(chat_id=ADMIN_ID, latitude=lat, longitude=lon)

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
        await query.edit_message_caption(caption=query.message.caption + "\n\n🟢 **TASDIQLANDI / ПОДТВЕРЖДЕНО**")

    elif action == "reject":
        msg = (
            "❌ To'lovingiz tasdiqlanmadi. Iltimos, chekni qaytadan tekshirib ko'ring yoki admin bilan bog'laning."
            if user_lang == "uz" else
            "❌ Ваша оплата не подтверждена. Пожалуйста, проверьте чек еще раз или свяжитесь с админом."
        )
        await context.bot.send_message(chat_id=user_id, text=msg)
        await query.edit_message_caption(caption=query.message.caption + "\n\n🔴 **RAD ETILDI / ОТКЛОНЕНО**")

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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, quantity_handler))

    print("Popcorn Haris boti ishga tushdi...")
    app.run_polling()
