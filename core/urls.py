from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/storefront/', views.home_storefront_filter, name='home_storefront_filter'),
    path('home/portfolio/', views.home_portfolio_filter, name='home_portfolio_filter'),
    path('about/', views.about, name='about'),
    path('service/', views.service, name='service'),
    path('contact/', views.contact, name='contact'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/content/', views.manage_content, name='manage_content'),
]