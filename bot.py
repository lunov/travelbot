from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Токен от @BotFather
TOKEN = "ВАШ_ТОКЕН_ЗДЕСЬ"

# Обработчик команды /start
async def start_command(update: Update, context):
    await update.message.reply_text("Привет! Я живой! 🚀")

# Обработчик обычных текстовых сообщений
async def echo(update: Update, context):
    user_text = update.message.text
    await update.message.reply_text(f"Вы написали: {user_text}")

# Настройка и запуск бота
def main():
    # Создаем приложение
    app = Application.builder().token(TOKEN).build()
    
    # Регистрируем обработчики команд
    app.add_handler(CommandHandler("start", start_command))
    
    # Регистрируем обработчик текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT, echo))
    
    # Запускаем бота
    print("Бот запущен! 🟢")
    app.run_polling()

if __name__ == "__main__":
    main()
