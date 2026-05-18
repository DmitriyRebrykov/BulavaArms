# apps/loyalty/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import LoyaltyAccount, LoyaltyTransaction
from apps.payments.models import Order

User = get_user_model()

# Процент бонусов от суммы заказа (по умолчанию 5%)
LOYALTY_EARN_PERCENTAGE = Decimal('5')


@receiver(post_save, sender=User)
def create_loyalty_account(sender, instance, created, **kwargs):
    """Создать бонусный счет при создании нового пользователя"""
    if created:
        LoyaltyAccount.objects.get_or_create(user=instance)


@receiver(post_save, sender=Order)
def process_loyalty_points(sender, instance, created, **kwargs):
    """
    Начислить бонусные поинты при оплате заказа.
    Вызывается после сохранения заказа.
    """
    # Начислять бонусы только для оплаченных заказов
    if instance.status == 'paid' and instance.user:
        try:
            loyalty_account = instance.user.loyalty_account
        except LoyaltyAccount.DoesNotExist:
            # Если счета нет, создать его
            loyalty_account = LoyaltyAccount.objects.create(user=instance.user)

        # Проверить, были ли уже начислены бонусы по этому заказу
        if instance.loyalty_transactions.filter(transaction_type='earn').exists():
            return

        # Расчет бонусов: (сумма заказа * процент) * мультиплікатор уровня
        base_points = instance.total * (LOYALTY_EARN_PERCENTAGE / Decimal('100'))
        multiplier = loyalty_account.get_tier_multiplier()
        points_to_earn = base_points * multiplier

        # Начислить бонусы
        loyalty_account.add_points(
            amount=points_to_earn,
            order=instance,
            description=f'Бонусы от замовлення #{instance.order_id} ({LOYALTY_EARN_PERCENTAGE}%)'
        )


def spend_loyalty_points_for_order(order, amount):
    """
    Списать бонусные поинты для скидки на заказ.
    Вызывается перед сохранением заказа при использовании бонусов.
    """
    if not order.user:
        return False

    try:
        loyalty_account = order.user.loyalty_account
    except LoyaltyAccount.DoesNotExist:
        return False

    if not loyalty_account.can_spend(amount):
        return False

    loyalty_account.spend_points(
        amount=amount,
        order=order,
        description=f'Использование бонусов в замовленні #{order.order_id}'
    )
    return True