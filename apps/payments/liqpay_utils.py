import base64
import hashlib
import json
from django.conf import settings


class LiqPayAPI:
    """
    Утилита для работы с LiqPay API.

    Основные методы:
    - create_payment_form() — генерирует data и signature для формы оплаты
    - verify_callback() — проверяет подпись callback от LiqPay
    """

    def __init__(self):
        self.public_key = settings.LIQPAY_PUBLIC_KEY
        self.private_key = settings.LIQPAY_PRIVATE_KEY

    def _generate_signature(self, data):
        """Генерирует signature для LiqPay (sha1 base64)"""
        sign_string = self.private_key + data + self.private_key
        signature = base64.b64encode(hashlib.sha1(sign_string.encode('utf-8')).digest()).decode('ascii')
        return signature

    def create_payment_form(self, order_id, amount, description, result_url, server_url):
        """
        Создаёт data и signature для формы оплаты LiqPay.

        Args:
            order_id: уникальный ID заказа
            amount: сумма в гривнах (float)
            description: описание платежа
            result_url: URL для возврата пользователя после оплаты
            server_url: URL для server callback (асинхронное уведомление)

        Returns:
            dict: {'data': '...', 'signature': '...'}
        """
        params = {
            'version': '3',
            'public_key': self.public_key,
            'action': 'pay',
            'amount': float(amount),
            'currency': 'UAH',
            'description': description,
            'order_id': order_id,
            'result_url': result_url,
            'server_url': server_url,
            'language': 'uk',  # украинский интерфейс
        }

        data = base64.b64encode(json.dumps(params).encode('utf-8')).decode('ascii')
        signature = self._generate_signature(data)

        return {
            'data': data,
            'signature': signature,
        }

    def verify_callback(self, data, signature):
        """
        Проверяет подпись callback от LiqPay.

        Args:
            data: base64 строка из POST запроса
            signature: подпись из POST запроса

        Returns:
            dict: декодированные данные если подпись верна, иначе None
        """
        # Проверяем подпись
        expected_signature = self._generate_signature(data)

        if signature != expected_signature:
            return None

        # Декодируем data
        try:
            decoded_data = base64.b64decode(data).decode('utf-8')
            return json.loads(decoded_data)
        except (ValueError, json.JSONDecodeError):
            return None

    def decode_data(self, data_base64):
        """
        Декодирует base64 data из LiqPay (для отладки).

        Args:
            data_base64: base64 строка

        Returns:
            dict: декодированные данные
        """
        try:
            decoded = base64.b64decode(data_base64).decode('utf-8')
            return json.loads(decoded)
        except:
            return {}