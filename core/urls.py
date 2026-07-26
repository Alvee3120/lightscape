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
    path('dashboard/contact-info/', views.manage_contact_info, name='manage_contact_info'),
    path('dashboard/services/', views.manage_services, name='manage_services'),
    path('dashboard/services/submit/', views.service_plan_create, name='service_plan_create'),
    path('dashboard/services/delete/<int:plan_id>/', views.service_plan_delete, name='service_plan_delete'),
    path('dashboard/services/<int:plan_id>/edit/', views.service_plan_edit, name='service_plan_edit'),
]