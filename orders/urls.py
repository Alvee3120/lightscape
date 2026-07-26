from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('download/free/<uuid:uid>/', views.request_free_download, name='request_free_download'),
    path('download/file/<uuid:token>/', views.serve_download, name='serve_download'),

    path('checkout/<uuid:uid>/', views.create_checkout_session, name='create_checkout_session'),
    path('sslcz/success/', views.sslcz_success, name='sslcz_success'),
    path('sslcz/fail/', views.sslcz_fail, name='sslcz_fail'),
    path('sslcz/cancel/', views.sslcz_cancel, name='sslcz_cancel'),
    path('sslcz/ipn/', views.sslcz_ipn, name='sslcz_ipn'),

    path('success/<uuid:order_id>/', views.order_success, name='order_success'),
]