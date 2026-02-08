from django.db.models import Q, Count
from django.shortcuts import render,get_object_or_404
from django.core.paginator import Paginator
from .models import Product, Category
from .filters import ProductFilter


def main(request):
    """Главная страница"""
    return render(request, 'main/main.html')


def catalog(request):
    products = Product.objects.all().select_related('category')

    category_slugs = request.GET.getlist('category')
    selected_categories = []
    if category_slugs:
        selected_categories = Category.objects.filter(slug__in=category_slugs)
        products = products.filter(category__slug__in=category_slugs)

    manufacturers = request.GET.getlist('manufacturer')
    if manufacturers:
        products = products.filter(manufacturer__in=manufacturers)

    calibers = request.GET.getlist('caliber')
    if calibers:
        products = products.filter(caliber__in=calibers)

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

    in_stock = request.GET.get('in_stock')
    if in_stock == 'true':
        products = products.filter(in_stock=True)

    status_discount = request.GET.get('status_discount')
    if status_discount == 'true':
        products = products.filter(status_discount=True)

    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(manufacturer__icontains=search_query)
        )

    sort_by = request.GET.get('sort', '-created_at')
    valid_sort_fields = [
        'price', '-price',
        'name', '-name',
        'created_at', '-created_at',
        'discount_price', '-discount_price'
    ]

    if sort_by in valid_sort_fields:
        products = products.order_by(sort_by)

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)


    all_categories = Category.objects.annotate(
        product_count=Count('products')
    ).filter(product_count__gt=0).order_by('name')

    base_query = Product.objects.all()
    if selected_categories:
        base_query = base_query.filter(category__in=selected_categories)

    manufacturers_with_count = base_query.values('manufacturer') \
        .annotate(count=Count('id')) \
        .filter(manufacturer__isnull=False) \
        .exclude(manufacturer='') \
        .order_by('manufacturer')

    # Калибры в рамках выбранных категорий
    calibers_with_count = base_query.values('caliber') \
        .annotate(count=Count('id')) \
        .filter(caliber__isnull=False) \
        .exclude(caliber='') \
        .order_by('caliber')

    # Статистика по наличию и скидкам
    in_stock_count = base_query.filter(in_stock=True).count()
    discount_count = base_query.filter(status_discount=True).count()

    context = {
        'products': page_obj,
        'categories': all_categories,
        'selected_categories': selected_categories,
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