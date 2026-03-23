from django.db import models
from django.conf import settings
from apps.main.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Очікування оплати'),
        ('paid', 'Оплачено'),
        ('cancelled', 'Відмінено'),
        ('refunded', 'Повернення'),
        ('processing', 'В обробці'),
    ]

    # Покупець (якщо авторизований)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='Покупець',
    )

    order_id = models.CharField(max_length=255, unique=True, verbose_name='Order ID')
    liqpay_payment_id = models.CharField(max_length=255, blank=True, verbose_name='LiqPay Payment ID')
    liqpay_order_id = models.CharField(max_length=255, blank=True, verbose_name='LiqPay Order ID')

    email = models.EmailField(blank=True, verbose_name='Email покупця')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    first_name = models.CharField(max_length=150, blank=True, verbose_name="Ім'я")
    last_name = models.CharField(max_length=150, blank=True, verbose_name='Прізвище')

    city = models.CharField(max_length=100, blank=True, verbose_name='Місто')
    postal_code = models.CharField(max_length=20, blank=True, verbose_name='Поштовий індекс')
    address = models.TextField(blank=True, verbose_name='Адреса')
    delivery_notes = models.TextField(blank=True, verbose_name='Коментар до замовлення')

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Сума товарів')
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Знижка')
    total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Разом до сплати')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')

    class Meta:
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'
        ordering = ['-created_at']

    def __str__(self):
        return f'Замовлення #{self.order_id} — {self.get_status_display()} — {self.total} ₴'

    def get_customer_name(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.email or 'Гість'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Замовлення')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name='Товар')

    product_name = models.CharField(max_length=200, verbose_name='Назва товару')
    quantity = models.PositiveIntegerField(verbose_name='Кількість')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Ціна за одиницю')

    class Meta:
        verbose_name = 'Позиція замовлення'
        verbose_name_plural = 'Позиції замовлення'

    def __str__(self):
        return f'{self.product_name} x{self.quantity}'

    @property
    def line_total(self):
        return self.unit_price * self.quantity