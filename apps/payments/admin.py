from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'quantity', 'unit_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'status', 'total', 'created_at', 'stripe_session_id')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'email', 'stripe_session_id', 'stripe_payment_intent')
    readonly_fields = ('stripe_session_id', 'stripe_payment_intent', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('Заказ', {
            'fields': ('id', 'status', 'email')
        }),
        ('Финансы', {
            'fields': ('subtotal', 'discount', 'total')
        }),
        ('Stripe', {
            'fields': ('stripe_session_id', 'stripe_payment_intent'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'quantity', 'unit_price')
    list_filter = ('order',)