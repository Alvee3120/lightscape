from django.shortcuts import render, get_object_or_404
from .models import Asset, Category, Portfolio
import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


def is_staff_user(user):
    return user.is_staff


@login_required(login_url='/admin-login/')
@user_passes_test(is_staff_user, login_url='/admin-login/')
def upload_page(request):
    return render(request, 'gallery/upload.html')


@login_required(login_url='/admin-login/')
@user_passes_test(is_staff_user, login_url='/admin-login/')
@require_POST
def upload_asset(request):
    """
    Handles ONE file per request (JS loops over selected files and
    calls this endpoint once per file, tracking progress separately).
    """
    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'No file provided'}, status=400)

    title = request.POST.get('title') or file.name.rsplit('.', 1)[0]

    asset = Asset.objects.create(
        title=title,
        original_file=file,
        is_free=True,
        is_published=True,
    )

    return JsonResponse({
        'success': True,
        'asset_id': asset.id,
        'title': asset.title,
        'edit_url': f'/admin/gallery/asset/{asset.id}/change/',
    })

def gallery_list(request):
    pricing = request.GET.get('pricing')
    assets = Asset.objects.filter(is_published=True)

    if pricing == 'free':
        assets = assets.filter(is_free=True)
    elif pricing == 'paid':
        assets = assets.filter(is_free=False)

    context = {
        'assets': assets,
        'active_pricing': pricing,
    }

    if request.htmx:
        return render(request, 'gallery/_gallery_content.html', context)

    return render(request, 'gallery/gallery_list.html', context)

def asset_detail(request, uid):
    asset = get_object_or_404(Asset, uid=uid, is_published=True)
    asset.view_count += 1
    asset.save(update_fields=['view_count'])
    return render(request, 'gallery/_asset_lightbox.html', {'asset': asset})

@login_required(login_url='/admin-login/')
@user_passes_test(is_staff_user, login_url='/admin-login/')
def portfolio_upload_page(request):
    categories = Category.objects.all()
    portfolio_items = Portfolio.objects.all()[:24]
    return render(request, 'gallery/portfolio_upload.html', {
        'categories': categories,
        'portfolio_items': portfolio_items,
    })


@login_required(login_url='/admin-login/')
@user_passes_test(is_staff_user, login_url='/admin-login/')
@require_POST
def portfolio_upload_submit(request):
    """Handles ONE file per request, same pattern as the storefront uploader."""
    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'No file provided'}, status=400)

    title = request.POST.get('title') or file.name.rsplit('.', 1)[0]
    category_id = request.POST.get('category') or None

    item = Portfolio.objects.create(
        title=title,
        original_file=file,
        category_id=category_id,
        is_published=True,
    )

    item.refresh_from_db()
    return JsonResponse({
        'success': True,
        'item_id': item.id,
        'title': item.title,
        'preview_url': item.preview_file.url if item.preview_file else '',
    })


@login_required(login_url='/admin-login/')
@user_passes_test(is_staff_user, login_url='/admin-login/')
@require_POST
def portfolio_delete(request, item_id):
    item = get_object_or_404(Portfolio, id=item_id)
    item.delete()
    return JsonResponse({'success': True})