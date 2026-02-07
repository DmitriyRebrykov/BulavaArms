from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'quantity', 'unit_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'email', 'status', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_id', 'email', 'phone', 'liqpay_payment_id', 'liqpay_order_id')
    readonly_fields = ('order_id', 'liqpay_payment_id', 'liqpay_order_id', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('Заказ', {
            'fields': ('order_id', 'status', 'email', 'phone')
        }),
        ('Финансы', {
            'fields': ('subtotal', 'discount', 'total')
        }),
        ('LiqPay', {
            'fields': ('liqpay_payment_id', 'liqpay_order_id'),
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