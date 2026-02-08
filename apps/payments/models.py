from django.db import models
from apps.main.models import Product


class Order(models.Model):
    """Заказ — создаётся при оплате через LiqPay"""

    STATUS_CHOICES = [
        ('pending', 'Ожидание оплаты'),
        ('paid', 'Оплачено'),
        ('cancelled', 'Отменено'),
        ('refunded', 'Возврат'),
        ('processing', 'В обработке'),
    ]

    # Уникальный идентификатор заказа для LiqPay
    order_id = models.CharField(max_length=255, unique=True, verbose_name='Order ID')

    # ID транзакции LiqPay (payment_id из callback)
    liqpay_payment_id = models.CharField(max_length=255, blank=True, verbose_name='LiqPay Payment ID')
    liqpay_order_id = models.CharField(max_length=255, blank=True, verbose_name='LiqPay Order ID')

    # Контактные данные
    email = models.EmailField(blank=True, verbose_name='Email покупателя')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    first_name = models.CharField(max_length=150, blank=True, verbose_name="Ім'я")
    last_name = models.CharField(max_length=150, blank=True, verbose_name='Прізвище')

    # Адрес доставки
    city = models.CharField(max_length=100, blank=True, verbose_name='Місто')
    postal_code = models.CharField(max_length=20, blank=True, verbose_name='Поштовий індекс')
    address = models.TextField(blank=True, verbose_name='Адреса')
    delivery_notes = models.TextField(blank=True, verbose_name='Коментар до замовлення')

    # Финансы (в гривнах)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Сумма товаров')
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Скидка')
    total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Итого к оплате')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.order_id} — {self.get_status_display()} — {self.total} ₴'

    def get_customer_name(self):
        """Получить полное имя покупателя"""
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.email or 'Гість'


class OrderItem(models.Model):
    """Позиция в заказе"""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name='Товар')

    # Снимок данных товара в момент покупки
    product_name = models.CharField(max_length=200, verbose_name='Название товара')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Цена за единицу')

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказов'

    def __str__(self):
        return f'{self.product_name} x{self.quantity}'

    @property
    def line_total(self):
        return self.unit_price * self.quantity