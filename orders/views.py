import os
from django.shortcuts import get_object_or_404, redirect, render
from django.http import FileResponse, Http404
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from gallery.models import Asset
from .models import DownloadToken
from django.conf import settings
from django.http import HttpResponse
from .models import Order, OrderItem

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .payment_gateway import create_payment_session, validate_transaction


def create_checkout_session(request, uid):
    asset = get_object_or_404(Asset, uid=uid, is_published=True)

    if asset.is_free:
        raise Http404("This asset is free, use the free download flow.")

    order = Order.objects.create(
        email=request.POST.get('email', 'guest@example.com'),
        amount_total=asset.price,
        status=Order.Status.PENDING,
    )
    OrderItem.objects.create(
        order=order,
        asset=asset,
        price_at_purchase=asset.price,
    )

    gateway_url = create_payment_session(order, request)

    if not gateway_url:
        order.status = Order.Status.FAILED
        order.save(update_fields=['status'])
        messages.error(request, "Could not start payment session. Please try again.")
        return redirect('gallery:gallery_list')

    return redirect(gateway_url)


def _mark_order_paid_if_valid(tran_id, val_id):
    """Shared logic used by both success callback and IPN."""
    try:
        order = Order.objects.get(order_id=tran_id)
    except Order.DoesNotExist:
        return None

    if order.status == Order.Status.PAID:
        return order  # already processed (IPN and success callback can both fire)

    result = validate_transaction(val_id)

    if result.get('status') in ('VALID', 'VALIDATED'):
        order.gateway_transaction_id = val_id
        order.mark_paid()

        for item in order.items.all():
            DownloadToken.objects.create(
                asset=item.asset,
                order=order,
                max_uses=3,
                expires_at=timezone.now() + timedelta(hours=48),
            )
    else:
        order.status = Order.Status.FAILED
        order.save(update_fields=['status'])

    return order


@csrf_exempt
@require_POST
def sslcz_success(request):
    tran_id = request.POST.get('tran_id')
    val_id = request.POST.get('val_id')
    order = _mark_order_paid_if_valid(tran_id, val_id)
    if order:
        return redirect('orders:order_success', order_id=order.order_id)
    return redirect('gallery:gallery_list')


@csrf_exempt
@require_POST
def sslcz_fail(request):
    tran_id = request.POST.get('tran_id')
    Order.objects.filter(order_id=tran_id).update(status=Order.Status.FAILED)
    messages.error(request, "Payment failed. Please try again.")
    return redirect('gallery:gallery_list')


@csrf_exempt
@require_POST
def sslcz_cancel(request):
    tran_id = request.POST.get('tran_id')
    Order.objects.filter(order_id=tran_id).update(status=Order.Status.CANCELLED)
    return redirect('gallery:gallery_list')


@csrf_exempt
@require_POST
def sslcz_ipn(request):
    """
    Server-to-server notification from SSLCommerz — the most reliable
    confirmation, independent of whether the customer's browser redirect worked.
    """
    tran_id = request.POST.get('tran_id')
    val_id = request.POST.get('val_id')
    _mark_order_paid_if_valid(tran_id, val_id)
    return HttpResponse(status=200)

def order_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    tokens = order.download_tokens.all() if order.status == Order.Status.PAID else []
    return render(request, 'orders/order_success.html', {'order': order, 'tokens': tokens})

def request_free_download(request, uid):
    """
    Called when user clicks 'Download Free' on a free asset.
    Generates a fresh DownloadToken and redirects to the actual
    protected file-serving URL.
    """
    asset = get_object_or_404(Asset, uid=uid, is_published=True)

    if not asset.is_free:
        raise Http404("This asset is not free.")

    token = DownloadToken.objects.create(
        asset=asset,
        order=None,  # free download, not tied to a purchase
        max_uses=3,
        expires_at=timezone.now() + timedelta(hours=48),
    )

    return redirect('orders:serve_download', token=token.token)


def serve_download(request, token):
    """
    The ONLY place original_file is ever served from.
    Validates the token before streaming the file.
    """
    download_token = get_object_or_404(DownloadToken, token=token)

    if not download_token.is_valid():
        return render_expired(request)

    # Register the use (increments counters) BEFORE streaming,
    # so a dropped connection still counts as "used" — safer against abuse
    download_token.register_use()

    asset = download_token.asset
    file_path = asset.original_file.path

    if not os.path.exists(file_path):
        raise Http404("File not found.")

    response = FileResponse(
        open(file_path, 'rb'),
        as_attachment=True,
        filename=f"{asset.slug}{os.path.splitext(file_path)[1]}"
    )
    return response


def render_expired(request):
    from django.shortcuts import render
    return render(request, 'orders/link_expired.html', status=410)