#основной модуль для работы телеграм бота
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from .handlers import BotHandlers
from .api_client import DeepSeekAPIClient
import logging

logger = logging.getLogger(__name__)

class DeepSeekBot:
    """Главный класс управления ботом"""
    
    def __init__(self, config):
        self.config = config
        
        # инициализация API клиента
        self.api_client = DeepSeekAPIClient(
            api_key=config.DEEPSEEK_API_KEY,
            api_url=config.DEEPSEEK_API_URL
        )
        
        # инициализация обработчиков
        self.handlers = BotHandlers(self.api_client)
        
        # создание приложения Telegram
        self.application = Application.builder().token(config.TELEGRAM_TOKEN).build()
        
        # регистрация обработчиков
        self._register_handlers()

    def _register_handlers(self):
        self.application.add_handler(CommandHandler("start", self.handlers.start))
        self.application.add_handler(CommandHandler("clear", self.handlers.clear_history))  # Новая команда
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.handle_message)
        )

    def run(self):
        logger.info("Бот запущен!")
        self.application.run_polling()
