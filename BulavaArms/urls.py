from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("apps.main.urls")),
    path('cart/', include("apps.cart.urls")),
    path('users/', include("apps.users.urls")),
    path('payments/', include("apps.payments.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
