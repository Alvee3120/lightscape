from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    path('', views.gallery_list, name='gallery_list'),
    path('asset/<uuid:uid>/', views.asset_detail, name='asset_detail'),
    path('upload/', views.upload_page, name='upload_page'),
    path('upload/submit/', views.upload_asset, name='upload_asset'),
    path('portfolio-upload/', views.portfolio_upload_page, name='portfolio_upload_page'),
    path('portfolio-upload/submit/', views.portfolio_upload_submit, name='portfolio_upload_submit'),
    path('portfolio-upload/delete/<int:item_id>/', views.portfolio_delete, name='portfolio_delete'),
]