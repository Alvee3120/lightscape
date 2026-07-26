from django.contrib import admin
from .models import Order, OrderItem, DownloadToken


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['asset', 'price_at_purchase']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'email', 'status', 'amount_total', 'created_at', 'paid_at']
    list_filter = ['status', 'created_at']
    search_fields = ['email', 'order_id', 'stripe_checkout_session_id']
    inlines = [OrderItemInline]


@admin.register(DownloadToken)
class DownloadTokenAdmin(admin.ModelAdmin):
    list_display = ['token', 'asset', 'order', 'use_count', 'max_uses', 'expires_at', 'is_revoked']
    list_filter = ['is_revoked']