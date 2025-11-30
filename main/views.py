from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Product, Category
from .filters import ProductFilter


def main(request):
    """Главная страница"""
    return render(request, 'main/main.html')


def catalog(request):
    """Каталог товаров с фильтрацией"""
    
    # Получаем все товары
    products = Product.objects.all().select_related('category')
    
    # Применяем фильтр
    product_filter = ProductFilter(request.GET, queryset=products)
    filtered_products = product_filter.qs
    
    # Сортировка
    sort_by = request.GET.get('sort', '-created_at')
    valid_sort_fields = [
        'price', '-price', 
        'name', '-name', 
        'created_at', '-created_at',
        'discount_price', '-discount_price'
    ]
    
    if sort_by in valid_sort_fields:
        filtered_products = filtered_products.order_by(sort_by)
    
    # Пагинация
    paginator = Paginator(filtered_products, 12)  # 12 товаров на страницу
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Получаем статистику для фильтров
    all_manufacturers = Product.objects.values_list('manufacturer', flat=True).distinct()
    manufacturers_with_count = []
    for manufacturer in all_manufacturers:
        if manufacturer:
            count = Product.objects.filter(manufacturer=manufacturer).count()
            manufacturers_with_count.append({
                'name': manufacturer,
                'count': count
            })
    
    all_calibers = Product.objects.values_list('caliber', flat=True).distinct()
    calibers_with_count = []
    for caliber in all_calibers:
        if caliber:
            count = Product.objects.filter(caliber=caliber).count()
            calibers_with_count.append({
                'name': caliber,
                'count': count
            })
    
    # Статистика по наличию
    in_stock_count = Product.objects.filter(in_stock=True).count()
    out_of_stock_count = Product.objects.filter(in_stock=False).count()
    
    context = {
        'products': page_obj,
        'filter': product_filter,
        'manufacturers': manufacturers_with_count,
        'calibers': calibers_with_count,
        'in_stock_count': in_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'total_count': filtered_products.count(),
        'categories': Category.objects.all(),
        'current_sort': sort_by,
    }
    
    return render(request, 'main/catalog.html', context)