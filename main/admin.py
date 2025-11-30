from django.contrib import admin
from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    """Inline для дополнительных изображений"""
    model = ProductImage
    extra = 3
    fields = ('image',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_type', 'category', 'price', 'discount_price', 'in_stock', 'status_discount', 'created_at')
    list_filter = ('product_type', 'category', 'in_stock', 'status_discount', 'manufacturer')
    search_fields = ('name', 'description', 'manufacturer', 'caliber')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('in_stock', 'status_discount')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description', 'product_type', 'category')
        }),
        ('Цены', {
            'fields': ('price', 'status_discount', 'discount_price')
        }),
        ('Характеристики', {
            'fields': ('manufacturer', 'color', 'size', 'material', 'caliber'),
            'classes': ('collapse',)
        }),
        ('Изображение и наличие', {
            'fields': ('main_image', 'in_stock')
        }),
    )
    
    inlines = [ProductImageInline]
    
    readonly_fields = ('created_at', 'updated_at')
    
    date_hierarchy = 'created_at'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')
    list_filter = ('product',)