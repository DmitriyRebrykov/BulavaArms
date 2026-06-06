# apps/loyalty/views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from decimal import Decimal
from .models import LoyaltyAccount


@login_required
@require_POST
def use_loyalty_points(request):
    """Використати бонуси при оплаті (викликається з checkout)"""
    try:
        amount = Decimal(request.POST.get('amount', 0))
        loyalty_account = LoyaltyAccount.objects.get(user=request.user)

        if not loyalty_account.can_spend(amount):
            return JsonResponse({
                'success': False,
                'message': f'Недостатньо бонусів. Доступно: {loyalty_account.balance} грн'
            })

        request.session['loyalty_points_to_use'] = str(amount)

        return JsonResponse({
            'success': True,
            'message': f'Бонуси в розмірі {amount} грн будуть використані',
            'remaining_balance': str(loyalty_account.balance - amount)
        })

    except LoyaltyAccount.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Бонусний рахунок не знайдено'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})