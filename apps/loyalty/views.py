# apps/loyalty/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
from .models import LoyaltyAccount, LoyaltyTransaction
from apps.payments.models import Order


@login_required
def loyalty_dashboard(request):
    """Панель управління бонусами"""
    loyalty_account = get_object_or_404(LoyaltyAccount, user=request.user)
    transactions = loyalty_account.transactions.all()[:20]

    # Расчет статистики
    stats = {
        'balance': loyalty_account.balance,
        'total_earned': loyalty_account.total_earned,
        'total_spent': loyalty_account.total_spent,
        'tier': loyalty_account.get_tier_display(),
        'tier_discount': loyalty_account.get_tier_discount(),
        'multiplier': loyalty_account.get_tier_multiplier(),
    }

    context = {
        'loyalty_account': loyalty_account,
        'transactions': transactions,
        'stats': stats,
    }
    return render(request, 'loyalty/dashboard.html', context)


@login_required
@require_POST
def use_loyalty_points(request):
    """Использовать бонусы при оплате"""
    try:
        amount = Decimal(request.POST.get('amount', 0))
        loyalty_account = get_object_or_404(LoyaltyAccount, user=request.user)

        if not loyalty_account.can_spend(amount):
            return JsonResponse({
                'success': False,
                'message': f'Недостатньо бонусів. Доступно: {loyalty_account.balance} грн'
            })

        # Бонусы будут списаны при подтверждении платежа
        request.session['loyalty_points_to_use'] = str(amount)

        return JsonResponse({
            'success': True,
            'message': f'Бонусы в размере {amount} грн будут использованы',
            'remaining_balance': str(loyalty_account.balance - amount)
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ошибка: {str(e)}'
        })


@login_required
def loyalty_transactions(request):
    """История всех операций с бонусами"""
    loyalty_account = get_object_or_404(LoyaltyAccount, user=request.user)
    transactions = loyalty_account.transactions.all().order_by('-created_at')

    # Фильтрация по типу операции
    transaction_type = request.GET.get('type')
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)

    context = {
        'transactions': transactions,
        'loyalty_account': loyalty_account,
    }
    return render(request, 'loyalty/transactions.html', context)


@login_required
def loyalty_tiers(request):
    """Информация о уровнях лояльности"""
    loyalty_account = get_object_or_404(LoyaltyAccount, user=request.user)

    tiers = [
        {
            'level': 'bronze',
            'name': 'Бронза',
            'requirement': 'От 0 грн',
            'multiplier': '1.0x',
            'discount': '0%',
            'perks': [
                'Базовые бонусы',
                'История покупок',
            ],
            'current': loyalty_account.tier == 'bronze'
        },
        {
            'level': 'silver',
            'name': 'Срібло',
            'requirement': 'От 20,000 грн',
            'multiplier': '1.25x',
            'discount': '2%',
            'perks': [
                'Увеличенные бонусы',
                'Скидка 2% на покупки',
                'Приоритетная поддержка',
            ],
            'current': loyalty_account.tier == 'silver'
        },
        {
            'level': 'gold',
            'name': 'Золото',
            'requirement': 'От 50,000 грн',
            'multiplier': '1.5x',
            'discount': '5%',
            'perks': [
                'Бонусы +50%',
                'Скидка 5% на покупки',
                'Бесплатная доставка',
                'Ранний доступ к акциям',
            ],
            'current': loyalty_account.tier == 'gold'
        },
        {
            'level': 'platinum',
            'name': 'Платина',
            'requirement': 'От 100,000 грн',
            'multiplier': '2.0x',
            'discount': '10%',
            'perks': [
                'Двойные бонусы',
                'Скидка 10% на покупки',
                'Бесплатная доставка',
                'Личный менеджер',
                'Ексклюзивные предложения',
            ],
            'current': loyalty_account.tier == 'platinum'
        },
    ]

    progress = {
        'total_spent': loyalty_account.total_spent,
        'next_tier': None,
        'progress_percentage': 0,
    }

    if loyalty_account.tier != 'platinum':
        tier_thresholds = {
            'bronze': 20000,
            'silver': 50000,
            'gold': 100000,
        }
        next_threshold = tier_thresholds.get(loyalty_account.tier, 20000)
        progress['next_tier'] = next_threshold
        progress['progress_percentage'] = min(
            int((loyalty_account.total_spent / next_threshold) * 100),
            99
        )

    context = {
        'loyalty_account': loyalty_account,
        'tiers': tiers,
        'progress': progress,
    }
    return render(request, 'loyalty/tiers.html', context)