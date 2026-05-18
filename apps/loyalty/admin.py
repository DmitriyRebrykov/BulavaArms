# apps/loyalty/admin.py
from django.contrib import admin
from .models import LoyaltyAccount, LoyaltyTransaction


class LoyaltyTransactionInline(admin.TabularInline):
    model = LoyaltyTransaction
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('transaction_type', 'amount', 'description', 'order', 'created_at')


@admin.register(LoyaltyAccount)
class LoyaltyAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'tier', 'total_earned', 'total_spent', 'updated_at')
    list_filter = ('tier', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'user__first_name')
    readonly_fields = ('created_at', 'updated_at', 'total_earned', 'total_spent')
    inlines = [LoyaltyTransactionInline]

    fieldsets = (
        ('Користувач', {
            'fields': ('user',)
        }),
        ('Баланс та статистика', {
            'fields': ('balance', 'total_earned', 'total_spent')
        }),
        ('Рівень та привілеї', {
            'fields': ('tier',)
        }),
        ('Дати', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    list_display = ('account', 'transaction_type', 'amount', 'description', 'created_at')
    list_filter = ('transaction_type', 'created_at', 'account__tier')
    search_fields = ('account__user__username', 'description')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Операція', {
            'fields': ('account', 'transaction_type', 'amount')
        }),
        ('Деталі', {
            'fields': ('description', 'order', 'created_at')
        }),
    )

    def has_add_permission(self, request):
        # Операції створюються автоматично, не через адмін
        return False