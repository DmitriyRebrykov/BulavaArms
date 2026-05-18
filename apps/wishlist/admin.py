# apps/wishlist/admin.py
from django.contrib import admin
from .models import Wishlist, WishlistItem


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
    readonly_fields = ('added_at',)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_items_count', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'user__first_name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [WishlistItemInline]

    def get_items_count(self, obj):
        return obj.items.count()
    get_items_count.short_description = 'Товарів у списку'


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'wishlist', 'added_at')
    list_filter = ('added_at', 'wishlist__user')
    search_fields = ('product__name', 'wishlist__user__username')
    readonly_fields = ('added_at',)