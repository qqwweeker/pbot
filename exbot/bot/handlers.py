#модуль обработчиков сообщений телеграма
from telegram import Update
from telegram.ext import ContextTypes
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BotHandlers:
    def __init__(self, api_client):
        self.api_client = api_client
        self.system_prompt = """Ты умный помощник в Telegram. Важные правила:
1. Запоминай контекст общения (историю диалога)
2. Если вопрос неполный, уточни его, используя предыдущие сообщения
3. Будь дружелюбным и помогай пользователю"""

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_text = """
        Привет! 👋 Я умный бот на основе DeepSeek.  

        Вот что я умею:  
        - Отвечать на вопросы с учётом контекста  
        - Запоминать историю диалога (до 10 сообщений)  
        - Очищать историю командой /clear   

        Просто напиши мне что-нибудь!  
        """
        await update.message.reply_text(welcome_text)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_message = update.message.text
        
        # инициализация истории
        if 'chat_history' not in context.user_data:
            context.user_data['chat_history'] = []
        
        # добавление вопроса
        context.user_data['chat_history'].append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # формирование системное сообщение и историю
        messages = [
            {"role": "system", "content": "Ты помощник. Отвечай кратко и по делу."},
            *context.user_data['chat_history'][-5:]  # Берем последние 5 реплик
        ]
        
        # запрос API
        response = self.api_client.get_response(messages)
        
        #ответ бота
        context.user_data['chat_history'].append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # ограничение истории до 10 сообщений
        context.user_data['chat_history'] = context.user_data['chat_history'][-10:]
        
        response = response.replace("###", "").replace("#", "")
        await update.message.reply_text(response, parse_mode="Markdown")

    async def clear_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if 'chat_history' in context.user_data:
            del context.user_data['chat_history']
        await update.message.reply_text("История диалога сброшена!")