from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Категория товаров"""
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='URL')
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Универсальный товар"""
    PRODUCT_TYPES = [
        ('weapon', 'Оружие'),
        ('ammunition', 'Патроны'),
        ('optics', 'Оптика'),
        ('clothing', 'Одежда'),
        ('equipment', 'Экипировка'),
    ]
    
    # Основные поля
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL')
    description = models.TextField(blank=True, verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    product_type = models.CharField(max_length=50, choices=PRODUCT_TYPES, verbose_name='Тип товара')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Категория')
    
    # Общие характеристики
    manufacturer = models.CharField(max_length=100, blank=True, verbose_name='Производитель')
    color = models.CharField(max_length=100, blank=True, verbose_name='Цвет')
    size = models.CharField(max_length=50, blank=True, verbose_name='Размер')
    material = models.CharField(max_length=200, blank=True, verbose_name='Материал')
    
    # Для оружия и патронов
    caliber = models.CharField(max_length=50, blank=True, verbose_name='Калибр')
    
    # Изображение и наличие
    main_image = models.ImageField(upload_to='products/', verbose_name='Главное изображение')
    in_stock = models.BooleanField(default=True, verbose_name='В наличии')
    
    # Скидка
    status_discount = models.BooleanField(default=False, verbose_name='Скидка')
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Цена со скидкой')
    
    # Даты
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """Дополнительные изображения товара"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='Товар')
    image = models.ImageField(upload_to='products/extra/', verbose_name='Изображение')
    
    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товара'