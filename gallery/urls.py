from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    path('', views.gallery_list, name='gallery_list'),
    path('portfolio/', views.portfolio_list, name='portfolio_list'),
    path('portfolio/<uuid:uid>/', views.portfolio_detail, name='portfolio_detail'),
    path('asset/<uuid:uid>/', views.asset_detail, name='asset_detail'),
    path('upload/', views.upload_page, name='upload_page'),
    path('upload/submit/', views.upload_asset, name='upload_asset'),
    path('upload/<int:asset_id>/edit/', views.asset_edit, name='asset_edit'),
    path('upload/delete/<int:asset_id>/', views.asset_delete, name='asset_delete'),
    path('portfolio-upload/', views.portfolio_upload_page, name='portfolio_upload_page'),
    path('portfolio-upload/submit/', views.portfolio_upload_submit, name='portfolio_upload_submit'),
    path('portfolio-upload/delete/<int:item_id>/', views.portfolio_delete, name='portfolio_delete'),
    path('portfolio-upload/<int:item_id>/edit/', views.portfolio_edit, name='portfolio_edit'),
    path('categories/', views.manage_categories, name='manage_categories'),
    path('categories/<int:category_id>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:category_id>/delete/', views.category_delete, name='category_delete'),
    path('tags/', views.manage_tags, name='manage_tags'),
    path('tags/<int:tag_id>/edit/', views.tag_edit, name='tag_edit'),
    path('tags/<int:tag_id>/delete/', views.tag_delete, name='tag_delete'),
]