import requests
import uuid
from django.conf import settings


def get_sslcz_url():
    if settings.SSLCZ_SANDBOX:
        return "https://sandbox.sslcommerz.com/gwprocess/v4/api.php"
    return "https://securepay.sslcommerz.com/gwprocess/v4/api.php"


def get_sslcz_validation_url():
    if settings.SSLCZ_SANDBOX:
        return "https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php"
    return "https://securepay.sslcommerz.com/validator/api/validationserverAPI.php"


def create_payment_session(order, request):
    """
    Calls SSLCommerz's session API to start a checkout.
    Returns the GatewayPageURL the customer should be redirected to.
    """
    tran_id = str(order.order_id)

    payload = {
        'store_id': settings.SSLCZ_STORE_ID,
        'store_passwd': settings.SSLCZ_STORE_PASSWORD,
        'total_amount': str(order.amount_total),
        'currency': 'BDT',
        'tran_id': tran_id,

        'success_url': request.build_absolute_uri(f'/orders/sslcz/success/'),
        'fail_url': request.build_absolute_uri(f'/orders/sslcz/fail/'),
        'cancel_url': request.build_absolute_uri(f'/orders/sslcz/cancel/'),
        'ipn_url': request.build_absolute_uri(f'/orders/sslcz/ipn/'),

        # Customer info (required by SSLCommerz even for digital goods)
        'cus_name': 'LightScape Customer',
        'cus_email': order.email,
        'cus_add1': 'N/A',
        'cus_city': 'Dhaka',
        'cus_postcode': '1200',
        'cus_country': 'Bangladesh',
        'cus_phone': '01700000000',

        # Product info
        'product_name': 'Digital Photo Download',
        'product_category': 'Digital Goods',
        'product_profile': 'general',

        'shipping_method': 'NO',
        'num_of_item': order.items.count(),
    }

    response = requests.post(get_sslcz_url(), data=payload, timeout=15)
    data = response.json()

    if data.get('status') == 'SUCCESS':
        order.gateway_session_id = data.get('sessionkey')
        order.save(update_fields=['gateway_session_id'])
        return data.get('GatewayPageURL')

    return None


def validate_transaction(val_id):
    """
    Confirms a transaction is genuinely paid by calling SSLCommerz's
    Validation API directly (never trust the browser redirect alone).
    """
    params = {
        'val_id': val_id,
        'store_id': settings.SSLCZ_STORE_ID,
        'store_passwd': settings.SSLCZ_STORE_PASSWORD,
        'format': 'json',
    }
    response = requests.get(get_sslcz_validation_url(), params=params, timeout=15)
    return response.json()