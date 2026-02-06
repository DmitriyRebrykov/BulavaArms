from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        verbose_name='Phone number'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Avatar'
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name='Date of birth'
    )
    address = models.TextField(
        blank=True,
        verbose_name='Address'
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='City'
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Postal code'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated at'
    )
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name or self.username
    
    def get_orders_count(self):
        return self.order_set.count() if hasattr(self, 'order_set') else 0