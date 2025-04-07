#Это модуль для взамодействия с апи дипсика
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
import time
from typing import List, Dict
import socket

logger = logging.getLogger(__name__)

class DeepSeekAPIClient:
    def __init__(self, api_key: str, api_url: str):
        self.api_key = api_key
        self.api_url = api_url
        
        # настройка сессии попыток
        self.session = requests.Session()
        
        # конфигурация попыток
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        
        # настройка адаптера
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=10,
            pool_block=False
        )
        
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # таймауты бота 3 сек на подключение, 30 сек на чтени
        self.timeout = (3.05, 30)
    def _prepare_headers(self) -> Dict:
        """Подготовка заголовков запроса"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "User-Agent": "DeepSeekBot/1.0"
        }

    def get_response(self, messages: List[Dict]) -> str:
        """Основной метод с улучшенным управлением соединениями"""
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.7
        }

        try:
            response = self.session.post(
                self.api_url,
                headers=self._prepare_headers(),
                json=payload,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {type(e).__name__}: {str(e)}")
            return self._handle_error(e)

    def _handle_error(self, error) -> str:
        """Обработка ошибок"""
        if isinstance(error, requests.exceptions.Timeout):
            return "Таймаут соединения. Попробуйте позже."
        elif isinstance(error, requests.exceptions.SSLError):
            return "Ошибка SSL. Попробуйте позже."
        elif isinstance(error, requests.exceptions.ConnectionError):
            return "Ошибка подключения. Проверьте интернет."
        elif isinstance(error, requests.exceptions.HTTPError):
            if error.response.status_code == 429:
                return "Слишком много запросов. Подождите минуту."
            return f"Ошибка API: {error.response.status_code}"
        else:
            return "Произошла неизвестная ошибка"

    def __del__(self):
        """заверщение работы"""
        self.session.close()