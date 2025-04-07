import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    filters,
    MessageHandler
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Константы для состояний
(MAIN_MENU, ROUTE_CHOICE, ZASLAVL, 
 STATION_BELARUS, MLYN, SOBOR, KOSTEL, FINAL) = range(8)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик команды /start"""
    keyboard = [[InlineKeyboardButton("Выбор маршрута", callback_data='route_choice')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text="Вітаем у боце «Спадарожнік»! Выберыце маршрут:",
        reply_markup=reply_markup
    )
    return MAIN_MENU

async def handle_route_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик выбора маршрута"""
    query = update.callback_query
    await query.answer()  # Важно: всегда отвечаем на callback_query
    
    keyboard = [
        [InlineKeyboardButton("Заславль", callback_data='zaslavl')],
        [InlineKeyboardButton("Раков", callback_data='rakov')],
        [InlineKeyboardButton("Раубичи", callback_data='raubichi')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="Выберыце маршрут:",
        reply_markup=reply_markup
    )
    return ROUTE_CHOICE

async def handle_zaslavl(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик выбора Заславля"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text="Вы выбрали маршрут по Заславлю!",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Начать", callback_data='start_route')]])
    )
    return ZASLAVL

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик отмены"""
    await update.message.reply_text("Действие отменено")
    return ConversationHandler.END

def main():
    """Настройка и запуск бота"""
    application = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(handle_route_choice, pattern='^route_choice$')
            ],
            ROUTE_CHOICE: [
                CallbackQueryHandler(handle_zaslavl, pattern='^zaslavl$'),
                CallbackQueryHandler(handle_route_choice, pattern='^back$')
            ],
            ZASLAVL: [
                CallbackQueryHandler(start, pattern='^start_route$')
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False
    )
    
    application.add_handler(conv_handler)
    application.add_error_handler(lambda u, c: logger.error(c.error))
    
    logger.info("Бот запущен в режиме polling...")
    application.run_polling()

if __name__ == '__main__':
    main()
