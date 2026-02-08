from django.db.models import Q, Count
from django.shortcuts import render,get_object_or_404
from django.core.paginator import Paginator
from .models import Product, Category
from .filters import ProductFilter


def main(request):
    """Главная страница"""
    return render(request, 'main/main.html')


def catalog(request):
    """Каталог товаров с фильтрацией по категориям"""

    # Получаем все товары
    products = Product.objects.all().select_related('category')

    # === ФИЛЬТРАЦИЯ ===

    # 1. Фильтр по категории
    category_slug = request.GET.get('category')
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    # 2. Фильтр по производителю (в рамках выбранной категории)
    manufacturers = request.GET.getlist('manufacturer')
    if manufacturers:
        products = products.filter(manufacturer__in=manufacturers)

    # 3. Фильтр по калибру
    calibers = request.GET.getlist('caliber')
    if calibers:
        products = products.filter(caliber__in=calibers)

    # 4. Фильтр по цене
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min:
        try:
            products = products.filter(price__gte=float(price_min))
        except ValueError:
            pass
    if price_max:
        try:
            products = products.filter(price__lte=float(price_max))
        except ValueError:
            pass

    # 5. Фильтр по наличию
    in_stock = request.GET.get('in_stock')
    if in_stock == 'true':
        products = products.filter(in_stock=True)

    # 6. Фильтр по скидке
    status_discount = request.GET.get('status_discount')
    if status_discount == 'true':
        products = products.filter(status_discount=True)

    # 7. Поиск
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(manufacturer__icontains=search_query)
        )

    # === СОРТИРОВКА ===
    sort_by = request.GET.get('sort', '-created_at')
    valid_sort_fields = [
        'price', '-price',
        'name', '-name',
        'created_at', '-created_at',
        'discount_price', '-discount_price'
    ]

    if sort_by in valid_sort_fields:
        products = products.order_by(sort_by)

    # === ПАГИНАЦИЯ ===
    paginator = Paginator(products, 12)  # 12 товаров на страницу
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # === СТАТИСТИКА ДЛЯ ФИЛЬТРОВ ===

    # Все категории с количеством товаров
    all_categories = Category.objects.annotate(
        product_count=Count('products')
    ).filter(product_count__gt=0).order_by('name')

    # Производители в рамках выбранной категории (или всех)
    base_query = Product.objects.all()
    if selected_category:
        base_query = base_query.filter(category=selected_category)

    manufacturers_with_count = base_query.values('manufacturer') \
        .annotate(count=Count('id')) \
        .filter(manufacturer__isnull=False) \
        .exclude(manufacturer='') \
        .order_by('manufacturer')

    # Калибры в рамках выбранной категории
    calibers_with_count = base_query.values('caliber') \
        .annotate(count=Count('id')) \
        .filter(caliber__isnull=False) \
        .exclude(caliber='') \
        .order_by('caliber')

    # Статистика по наличию
    in_stock_count = base_query.filter(in_stock=True).count()
    discount_count = base_query.filter(status_discount=True).count()

    context = {
        'products': page_obj,
        'categories': all_categories,
        'selected_category': selected_category,
        'manufacturers': manufacturers_with_count,
        'calibers': calibers_with_count,
        'in_stock_count': in_stock_count,
        'discount_count': discount_count,
        'total_count': products.count(),
        'current_sort': sort_by,
        'search_query': search_query,
    }

    return render(request, 'main/catalog.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request,'main/product-detail.html', {'product':product})