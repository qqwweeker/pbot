#запуск бота
from bot.bot import DeepSeekBot
from config import Config
import logging

#настройка базового логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

if __name__ == "__main__":
    #инициализация конфигурации
    config = Config()
    
    #запуск бота
    bot = DeepSeekBot(config)
    bot.run()