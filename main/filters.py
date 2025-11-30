import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    """Фильтр для товаров"""
    
    # Фильтр по названию (поиск)
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Поиск по названию'
    )
    
    # Фильтр по производителю (бренду)
    manufacturer = django_filters.MultipleChoiceFilter(
        choices=[],  # Будет заполнено динамически
        label='Производитель'
    )
    
    # Фильтр по калибру
    caliber = django_filters.MultipleChoiceFilter(
        choices=[],  # Будет заполнено динамически
        label='Калибр'
    )
    
    # Фильтр по цене (диапазон)
    price_min = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte',
        label='Цена от'
    )
    
    price_max = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte',
        label='Цена до'
    )
    
    # Фильтр по наличию
    in_stock = django_filters.BooleanFilter(
        label='В наличии'
    )
    
    # Фильтр по скидке
    status_discount = django_filters.BooleanFilter(
        label='Товары со скидкой'
    )
    
    # Фильтр по категории
    category = django_filters.ModelMultipleChoiceFilter(
        queryset=None,  # Будет установлено в __init__
        label='Категория'
    )
    
    # Фильтр по типу товара
    product_type = django_filters.MultipleChoiceFilter(
        choices=Product.PRODUCT_TYPES,
        label='Тип товара'
    )
    
    class Meta:
        model = Product
        fields = ['manufacturer', 'caliber', 'in_stock', 'status_discount', 
                  'category', 'product_type']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Динамически получаем уникальные производители
        manufacturers = Product.objects.values_list('manufacturer', flat=True).distinct()
        manufacturer_choices = [(m, m) for m in manufacturers if m]
        self.filters['manufacturer'].extra['choices'] = manufacturer_choices
        
        # Динамически получаем уникальные калибры
        calibers = Product.objects.values_list('caliber', flat=True).distinct()
        caliber_choices = [(c, c) for c in calibers if c]
        self.filters['caliber'].extra['choices'] = caliber_choices
        
        # Устанавливаем queryset для категорий
        from .models import Category
        self.filters['category'].queryset = Category.objects.all()