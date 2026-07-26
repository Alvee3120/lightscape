
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('gallery/', include('gallery.urls')),
    path('orders/', include('orders.urls')),

    path('admin-login/', auth_views.LoginView.as_view(template_name='core/admin_login.html', redirect_authenticated_user=True), name='admin_login'),
    path('admin-logout/', auth_views.LogoutView.as_view(next_page='admin_login'), name='admin_logout'),

    path('', include('core.urls')),
]

# Served directly by Django regardless of DEBUG: WhiteNoise only covers
# STATIC_URL, and this project has no external storage (S3/Cloudinary) for
# user-uploaded media yet, so this is the simplest way to serve it on Render.
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]