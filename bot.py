import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    ConversationHandler,
    Dispatcher
)
from flask import Flask, request
from waitress import serve

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Константы для состояний
(MAIN_MENU, ROUTE_CHOICE, ZASLAVL, 
 STATION_BELARUS, MLYN, SOBOR, KOSTEL, FINAL) = range(8)

# Инициализация Flask
app = Flask(__name__)

# Конфигурация
TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TOKEN:
    raise ValueError("Не задан TELEGRAM_TOKEN в переменных окружения")

PORT = int(os.environ.get('PORT', 8000))
WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'https://independent-trust.up.railway.app')

# Инициализация бота
updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

def setup_webhook():
    """Принудительная установка вебхука при запуске"""
    try:
        # Удаляем старый вебхук
        updater.bot.delete_webhook()
        
        # Устанавливаем новый вебхук
        webhook_url = f"{WEBHOOK_URL}/webhook"
        success = updater.bot.set_webhook(
            url=webhook_url,
            max_connections=40,
            drop_pending_updates=True
        )
        
        if success:
            logger.info(f"✅ Вебхук установлен: {webhook_url}")
            webhook_info = updater.bot.get_webhook_info()
            logger.info(f"ℹ️ Статус вебхука: {webhook_info}")
        else:
            logger.error("❌ Не удалось установить вебхук")
            
    except Exception as e:
        logger.critical(f"🔥 Ошибка при настройке вебхука: {str(e)}")
        raise

# ========== ОБРАБОТЧИКИ КОМАНД ========== #

def start(update: Update, context: CallbackContext) -> int:
    """Обработчик команды /start"""
    photo_url = 'https://img.goodfon.com/original/2388x1668/a/44/sputnik-1-1957-sputnik-1.jpg'
    caption = "Вітаем у боце «Спадарожнік»! Гэты бот дапаможа вам адкрыць для сябе цікавыя маршруты."

    keyboard = [[InlineKeyboardButton("Выбор маршрута", callback_data='route_choice')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_photo(
        photo=photo_url,
        caption=caption,
        reply_markup=reply_markup
    )
    return MAIN_MENU

def route_choice(update: Update, context: CallbackContext) -> int:
    """Обработчик выбора маршрута"""
    query = update.callback_query
    query.answer()

    text = "Выберыце маршрут, каб даведацца больш:"
    keyboard = [
        [InlineKeyboardButton("Заславль", callback_data='zaslavl')],
        [InlineKeyboardButton("Раков", callback_data='rakov')],
        [InlineKeyboardButton("Раубичи", callback_data='raubichi')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(text=text, reply_markup=reply_markup)
    return ROUTE_CHOICE

def route_in_development(update: Update, context: CallbackContext) -> int:
    """Обработчик для маршрутов в разработке"""
    query = update.callback_query
    query.answer()

    text = "Извините, маршруты в разработке."
    keyboard = [[InlineKeyboardButton("Назад", callback_data='back_to_routes')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(text=text, reply_markup=reply_markup)
    return ROUTE_CHOICE

def zaslavl_info(update: Update, context: CallbackContext) -> int:
    """Информация о маршруте Заславль"""
    query = update.callback_query
    query.answer()

    text = ("Маршрут «Заславль»:\n\n"
            "Горад-музей пад адкрытым небам з багатай гісторыяй і цікавымі помнікамі архітэктуры.")
    keyboard = [[InlineKeyboardButton("Пачаць", callback_data='station_belarus')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(text=text, reply_markup=reply_markup)
    return ZASLAVL

def station_belarus(update: Update, context: CallbackContext) -> int:
    """Станция Беларусь"""
    query = update.callback_query
    query.answer()

    media = [InputMediaPhoto(
        'https://avatars.mds.yandex.net/get-altay/4546519/2a0000017c5b6f2b03411f81c36c607e2985/XXXL',
        caption="Станцыя «Беларусь». Тут вы можаце пачаць сваё падарожжа.")]

    keyboard = [
        [InlineKeyboardButton("Далей", callback_data='mlyn')],
        [InlineKeyboardButton("Выбар маршрута", callback_data='back_to_routes')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.message.reply_media_group(media=media)
    query.message.reply_text(
        text="Станцыя «Беларусь» - пачатак вашага маршруту.",
        reply_markup=reply_markup
    )
    return STATION_BELARUS

def mlyn(update: Update, context: CallbackContext) -> int:
    """Млын"""
    query = update.callback_query
    query.answer()

    media = [InputMediaPhoto(
        'https://photocentra.ru/images/main77/771668_main.jpg',
        caption="Млын - помнік індустрыяльнай архітэктуры.")]

    keyboard = [
        [InlineKeyboardButton("Назад", callback_data='station_belarus'),
         InlineKeyboardButton("Далей", callback_data='sobor')],
        [InlineKeyboardButton("Выбар маршрута", callback_data='back_to_routes')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.message.reply_media_group(media=media)
    query.message.reply_text(
        text="Млын - цікавы помнік індустрыяльнай архітэктуры Заслаўля.",
        reply_markup=reply_markup
    )
    return MLYN

def sobor(update: Update, context: CallbackContext) -> int:
    """Собор"""
    query = update.callback_query
    query.answer()

    media = [InputMediaPhoto(
        'https://azbyka.ru/palomnik/images/b/b7/Преображенская_церковь_заславль1.jpg',
        caption="Спаса-Праабражэнскі сабор - цэнтр духоўнага жыцця горада.")]

    keyboard = [
        [InlineKeyboardButton("Назад", callback_data='mlyn'),
         InlineKeyboardButton("Далей", callback_data='kostel')],
        [InlineKeyboardButton("Выбар маршрута", callback_data='back_to_routes')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.message.reply_media_group(media=media)
    query.message.reply_text(
        text="Спаса-Праабражэнскі сабор - цэнтр духоўнага жыцця Заслаўля.",
        reply_markup=reply_markup
    )
    return SOBOR

def kostel(update: Update, context: CallbackContext) -> int:
    """Костёл"""
    query = update.callback_query
    query.answer()

    media = [InputMediaPhoto(
        'https://belarustut.by/wp-content/uploads/slider52/2-min.jpeg',
        caption="Касцёл Ражства Дзевы Марыі - помнік архітэктуры XVI стагоддзя.")]

    keyboard = [
        [InlineKeyboardButton("Назад", callback_data='sobor'),
         InlineKeyboardButton("Далей", callback_data='final')],
        [InlineKeyboardButton("Выбар маршрута", callback_data='back_to_routes')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.message.reply_media_group(media=media)
    query.message.reply_text(
        text="Касцёл Ражства Дзевы Марыі - помнік архітэктуры XVI стагоддзя.",
        reply_markup=reply_markup
    )
    return KOSTEL

def final(update: Update, context: CallbackContext) -> int:
    """Завершение маршрута"""
    query = update.callback_query
    query.answer()

    media = [InputMediaPhoto(
        'https://avatars.mds.yandex.net/get-altay/1246719/2a000001642aaf3789301a7bd185a8c7256c/XXL_height',
        caption="Дзякуем за падарожжа па Заслаўлю!")]

    keyboard = [
        [InlineKeyboardButton("Назад", callback_data='kostel')],
        [InlineKeyboardButton("Выбар маршрута", callback_data='back_to_routes')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.message.reply_media_group(media=media)
    query.message.reply_text(
        text="Дзякуем, што абралі маршрут «Заславль»! Спадзяемся, вам спадабалася.",
        reply_markup=reply_markup
    )
    return FINAL

# ========== WEBHOOK И ЗАПУСК ========== #

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        try:
            json_data = request.get_json()
            update = Update.de_json(json_data, updater.bot)
            dp.process_update(update)
            logger.info("✅ Сообщение обработано")
            return 'ok', 200
        except Exception as e:
            logger.error(f"❌ Ошибка обработки: {str(e)}")
            return 'error', 200
    
    return "Используйте POST для Telegram webhook", 200

@app.route('/')
def index():
    return f"Бот работает! Вебхук: {WEBHOOK_URL}/webhook", 200

@app.route('/set_webhook')
def set_webhook_route():
    """Ручная установка вебхука через браузер"""
    setup_webhook()
    return "Вебхук установлен", 200

def setup_dispatcher():
    """Настройка обработчиков"""
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [CallbackQueryHandler(route_choice, pattern='^route_choice$')],
            ROUTE_CHOICE: [
                CallbackQueryHandler(zaslavl_info, pattern='^zaslavl$'),
                CallbackQueryHandler(route_in_development, pattern='^rakov$'),
                CallbackQueryHandler(route_in_development, pattern='^raubichi$'),
                CallbackQueryHandler(route_choice, pattern='^back_to_routes$')
            ],
            ZASLAVL: [CallbackQueryHandler(station_belarus, pattern='^station_belarus$')],
            STATION_BELARUS: [
                CallbackQueryHandler(mlyn, pattern='^mlyn$'),
                CallbackQueryHandler(route_choice, pattern='^back_to_routes$')
            ],
            MLYN: [
                CallbackQueryHandler(station_belarus, pattern='^station_belarus$'),
                CallbackQueryHandler(sobor, pattern='^sobor$'),
                CallbackQueryHandler(route_choice, pattern='^back_to_routes$')
            ],
            SOBOR: [
                CallbackQueryHandler(mlyn, pattern='^mlyn$'),
                CallbackQueryHandler(kostel, pattern='^kostel$'),
                CallbackQueryHandler(route_choice, pattern='^back_to_routes$')
            ],
            KOSTEL: [
                CallbackQueryHandler(sobor, pattern='^sobor$'),
                CallbackQueryHandler(final, pattern='^final$'),
                CallbackQueryHandler(route_choice, pattern='^back_to_routes$')
            ],
            FINAL: [
                CallbackQueryHandler(kostel, pattern='^kostel$'),
                CallbackQueryHandler(route_choice, pattern='^back_to_routes$')
            ]
        },
        fallbacks=[CommandHandler('start', start)],
    )
    dp.add_handler(conv_handler)

if __name__ == '__main__':
    # Настройка обработчиков
    setup_dispatcher()
    
    # Установка вебхука
    setup_webhook()
    
    # Запуск сервера
    logger.info(f"🚀 Сервер запущен на порту {PORT}")
    serve(app, host="0.0.0.0", port=PORT)
