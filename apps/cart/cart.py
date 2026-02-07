# cart/cart.py
from decimal import Decimal
from django.conf import settings
from apps.main.models import Product


class Cart:
    """Сесійна корзина для товарів"""
    
    def __init__(self, request):
        """
        Ініціалізація корзини
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        
        if not cart:
            # Зберегти порожню корзину в сесії
            cart = self.session[settings.CART_SESSION_ID] = {}
        
        self.cart = cart
    
    def add(self, product, quantity=1, override_quantity=False):
        """
        Додати товар до корзини або оновити його кількість

        Args:
            product: об'єкт Product
            quantity: кількість товару
            override_quantity: якщо True - замінити кількість, інакше - додати
        """
        product_id = str(product.id)
        
        if product_id not in self.cart:
            if product.status_discount and product.discount_price:
                price = str(product.discount_price)
            else:
                price = str(product.price)
            
            self.cart[product_id] = {
                'quantity': 0,
                'price': price,
            }
        
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        
        self.save()
    
    def save(self):
        """Зберегти корзину в сесії"""
        self.session.modified = True
    
    def remove(self, product):
        """
        Видалити товар з корзини
        
        Args:
            product: об'єкт Product або product_id
        """
        product_id = str(product.id if hasattr(product, 'id') else product)
        
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def update_quantity(self, product_id, quantity):
        """
        Оновити кількість товару
        
        Args:
            product_id: ID товару
            quantity: нова кількість
        """
        product_id = str(product_id)
        
        if product_id in self.cart:
            if quantity > 0:
                self.cart[product_id]['quantity'] = quantity
            else:
                del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids) \
            .select_related('category')

        for product in products:
            # Беремо копію, щоб не змінювати оригінал
            item = self.cart[str(product.id)].copy()
            item['product'] = product

            price = Decimal(item['price'])
            quantity = item['quantity']

            item['price'] = price  # тільки в тимчасовому словнику
            item['total_price'] = price * quantity

            yield item
    
    def __len__(self):
        """
        Підрахувати загальну кількість товарів у корзині
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def get_subtotal(self):
        """
        Підрахувати суму без знижок (оригінальні ціни)
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        
        subtotal = Decimal('0')
        for product in products:
            product_id = str(product.id)
            if product_id in self.cart:
                quantity = self.cart[product_id]['quantity']
                subtotal += product.price * quantity
        
        return subtotal
    
    def get_discount(self):
        """
        Підрахувати загальну знижку
        """
        return self.get_subtotal() - self.get_total_price()
    
    def clear(self):
        """
        Очистити корзину
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()
    
    def get_items_count(self):
        """
        Отримати кількість товарів (для відображення в header)
        """
        return len(self)
    
    def has_products(self):
        """
        Перевірити чи є товари в корзині
        """
        return len(self.cart) > 0