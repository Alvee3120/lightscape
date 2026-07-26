
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('gallery/', include('gallery.urls')),
    path('orders/', include('orders.urls')),

    path('admin-login/', auth_views.LoginView.as_view(template_name='core/admin_login.html'), name='admin_login'),
    path('admin-logout/', auth_views.LogoutView.as_view(next_page='admin_login'), name='admin_logout'),
    
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)