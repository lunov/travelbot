import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния диалога
MAIN_MENU, ROUTE_CHOICE = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало взаимодействия - команда /start"""
    if not update.message:
        await update.callback_query.answer()
        return MAIN_MENU
        
    keyboard = [[InlineKeyboardButton("Выбор маршрута", callback_data='route_choice')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text="Вітаем у боце «Спадарожнік»! Выберыце маршрут:",
        reply_markup=reply_markup
    )
    return MAIN_MENU

async def route_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик выбора маршрута"""
    query = update.callback_query
    await query.answer()  # Обязательно отвечаем на callback
    
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
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик отмены"""
    if update.message:
        await update.message.reply_text("Действие отменено")
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("Действие отменено")
    return ConversationHandler.END

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    logger.error(f'Ошибка: {context.error}', exc_info=context.error)
    if update.callback_query:
        await update.callback_query.answer("Произошла ошибка, попробуйте позже")

def main() -> None:
    """Запуск бота"""
    # Убедитесь, что токен установлен
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        raise ValueError("Не указан TELEGRAM_TOKEN")
    
    # Создаем Application
    application = Application.builder().token(token).build()
    
    # Настраиваем обработчики
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(route_choice, pattern='^route_choice$')
            ],
            ROUTE_CHOICE: [
                CallbackQueryHandler(handle_zaslavl, pattern='^zaslavl$'),
                CallbackQueryHandler(cancel, pattern='^cancel$')
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False
    )
    
    # Добавляем обработчики
    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    logger.info("Бот запущен в режиме polling...")
    application.run_polling(drop_pending_updates=True)  # Важно для избежания конфликтов

if __name__ == '__main__':
    main()
