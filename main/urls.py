from django.urls import path
from .views import catalog, main

app_name = 'main'

urlpatterns = [
    path('', main, name='main_page'),
    path('catalog', catalog, name='catalog'),
]
