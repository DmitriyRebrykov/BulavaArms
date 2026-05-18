# apps/wishlist/models.py
from django.db import models
from django.conf import settings
from apps.main.models import Product


class Wishlist(models.Model):
    """Основная модель списка желаний пользователя"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlist',
        verbose_name='Користувач'
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
        verbose_name = 'Список бажань'
        verbose_name_plural = 'Списки бажань'
        ordering = ['-updated_at']

    def __str__(self):
        return f'Список бажань {self.user.get_full_name()}'

    def add_product(self, product):
        """Додати товар до списку бажань"""
        if not self.items.filter(product=product).exists():
            WishlistItem.objects.create(wishlist=self, product=product)
            return True
        return False

    def remove_product(self, product):
        """Видалити товар зі списку бажань"""
        deleted_count, _ = self.items.filter(product=product).delete()
        return deleted_count > 0

    def toggle_product(self, product):
        """Додати або видалити товар (переключити)"""
        if self.items.filter(product=product).exists():
            return self.remove_product(product), False
        else:
            return self.add_product(product), True

    def clear(self):
        """Очистити весь список"""
        self.items.all().delete()

    def get_products_count(self):
        """Отримати кількість товарів у списку"""
        return self.items.count()

    def has_product(self, product):
        """Перевірити чи товар у списку"""
        return self.items.filter(product=product).exists()


class WishlistItem(models.Model):
    """Товари у списку бажань"""
    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Список бажань'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='in_wishlists',
        verbose_name='Товар'
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата додавання'
    )

    class Meta:
        verbose_name = 'Елемент списку'
        verbose_name_plural = 'Елементи списку'
        ordering = ['-added_at']
        unique_together = ('wishlist', 'product')

    def __str__(self):
        return f'{self.product.name} в списку {self.wishlist.user.username}'