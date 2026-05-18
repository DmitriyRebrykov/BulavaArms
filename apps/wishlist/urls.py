from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    path('', views.wishlist_view, name='wishlist_detail'),
    path('add/<int:product_id>/', views.add_to_wishlist, name='add'),
    path('remove/<int:product_id>/', views.remove_from_wishlist, name='remove'),
    path('toggle/<int:product_id>/', views.toggle_wishlist, name='toggle'),
    path('check/<int:product_id>/', views.check_in_wishlist, name='check'),
    path('clear/', views.wishlist_clear, name='clear'),
]