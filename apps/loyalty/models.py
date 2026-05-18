# apps/loyalty/models.py
from django.db import models
from django.conf import settings
from decimal import Decimal


class LoyaltyAccount(models.Model):
    """Бонусный счёт пользователя"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='loyalty_account',
        verbose_name='Користувач'
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Баланс бонусів'
    )
    total_earned = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Всього заробллено'
    )
    total_spent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Всього витрачено'
    )
    tier = models.CharField(
        max_length=20,
        choices=[
            ('bronze', 'Бронза'),
            ('silver', 'Срібло'),
            ('gold', 'Золото'),
            ('platinum', 'Платина'),
        ],
        default='bronze',
        verbose_name='Рівень'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата створення'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата оновлення'
    )

    class Meta:
        verbose_name = 'Бонусний рахунок'
        verbose_name_plural = 'Бонусні рахунки'

    def __str__(self):
        return f'Бонусний рахунок {self.user.get_full_name()} ({self.balance} грн)'

    def add_points(self, amount, order=None, description=''):
        """Додати бонусні поінти"""
        transaction = LoyaltyTransaction.objects.create(
            account=self,
            transaction_type='earn',
            amount=amount,
            order=order,
            description=description or 'Бонуси від замовлення'
        )
        self.balance += amount
        self.total_earned += amount
        self._update_tier()
        self.save()
        return transaction

    def spend_points(self, amount, order=None, description=''):
        """Витратити бонусні поінти"""
        if self.balance < amount:
            raise ValueError('Недостатньо бонусів')

        transaction = LoyaltyTransaction.objects.create(
            account=self,
            transaction_type='spend',
            amount=amount,
            order=order,
            description=description or 'Використання бонусів'
        )
        self.balance -= amount
        self.total_spent += amount
        self._update_tier()
        self.save()
        return transaction

    def _update_tier(self):
        """Оновити рівень на основі витраченої суми"""
        if self.total_spent >= 100000:
            self.tier = 'platinum'
        elif self.total_spent >= 50000:
            self.tier = 'gold'
        elif self.total_spent >= 20000:
            self.tier = 'silver'
        else:
            self.tier = 'bronze'

    def get_tier_multiplier(self):
        """Отримати мультиплікатор бонусів за рівнем"""
        multipliers = {
            'bronze': Decimal('1.0'),
            'silver': Decimal('1.25'),
            'gold': Decimal('1.5'),
            'platinum': Decimal('2.0'),
        }
        return multipliers.get(self.tier, Decimal('1.0'))

    def get_tier_discount(self):
        """Отримати знижку за рівнем (в процентах)"""
        discounts = {
            'bronze': Decimal('0'),
            'silver': Decimal('2'),
            'gold': Decimal('5'),
            'platinum': Decimal('10'),
        }
        return discounts.get(self.tier, Decimal('0'))

    def can_spend(self, amount):
        """Перевірити чи достатньо бонусів"""
        return self.balance >= amount


class LoyaltyTransaction(models.Model):
    """Історія операцій з бонусами"""
    TRANSACTION_TYPES = [
        ('earn', 'Заробити'),
        ('spend', 'Витратити'),
        ('adjustment', 'Коригування'),
        ('expire', 'Закінчення'),
    ]

    account = models.ForeignKey(
        LoyaltyAccount,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='Бонусний рахунок'
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
        verbose_name='Тип операції'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Сума'
    )
    description = models.TextField(
        default='',
        blank=True,
        verbose_name='Опис'
    )
    order = models.ForeignKey(
        'payments.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='loyalty_transactions',
        verbose_name='Замовлення'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата операції'
    )

    class Meta:
        verbose_name = 'Операція лояльності'
        verbose_name_plural = 'Операції лояльності'
        ordering = ['-created_at']

    def __str__(self):
        action = 'Начислено' if self.transaction_type == 'earn' else 'Списано'
        return f'{action} {self.amount} грн — {self.created_at.strftime("%d.%m.%Y")}'