from django.urls import path
from .views import catalog, main, product_detail

app_name = 'main'

urlpatterns = [
    path('', main, name='main_page'),
    path('catalog', catalog, name='catalog'),
    path('<slug:slug>', product_detail, name='detail_page')
]
