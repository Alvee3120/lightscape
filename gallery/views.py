from decimal import Decimal, InvalidOperation
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from .models import Asset, Category, Tag, Portfolio
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST


def is_staff_user(user):
    return user.is_staff


@login_required(login_url='/admin-login/')
@user_passes_test(is_staff_user, login_url='/admin-login/')
def upload_page(request):
    assets = Asset.objects.all()
    return render(request, 'gallery/upload.html', {
        'assets': assets,
        'active_nav': 'storefront',
    })


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
    is_free = request.POST.get('is_free') == 'on'

    if is_free:
        price = Decimal('0.00')
    else:
        try:
            price = Decimal(request.POST.get('price', '0').strip() or '0')
        except InvalidOperation:
            return JsonResponse({'error': 'Price must be a valid number'}, status=400)

    asset = Asset.objects.create(
        title=title,
        original_file=file,
        is_free=is_free,
        price=price,
        is_published=True,
    )

    asset.refresh_from_db()
    return JsonResponse({
        'success': True,
        'asset_id': asset.id,
        'title': asset.title,
        'preview_url': asset.preview_file.url if asset.preview_file else '',
        'is_free': asset.is_free,
        'price': str(asset.price),
        'edit_url': reverse('gallery:asset_edit', args=[asset.id]),
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
def asset_edit(request, asset_id):
    asset = get_object_or_404(Asset, id=asset_id)
    all_tags = Tag.objects.all()

    if request.method == 'POST':
        asset.title = request.POST.get('title', '').strip()
        asset.description = request.POST.get('description', '').strip()
        asset.is_published = request.POST.get('is_published') == 'on'
        is_free = request.POST.get('is_free') == 'on'

        if is_free:
            price = Decimal('0.00')
        else:
            try:
                price = Decimal(request.POST.get('price', '0').strip() or '0')
            except InvalidOperation:
                messages.error(request, 'Price must be a valid number.')
                return render(request, 'gallery/asset_edit.html', {
                    'asset': asset, 'all_tags': all_tags, 'active_nav': 'storefront',
                })

        asset.is_free = is_free
        asset.price = price
        asset.save()
        asset.tags.set(request.POST.getlist('tags'))

        messages.success(request, 'Asset updated.')
        return redirect('gallery:upload_page')

    return render(request, 'gallery/asset_edit.html', {
        'asset': asset, 'all_tags': all_tags, 'active_nav': 'storefront',
    })


@login_required(login_url='/admin-login/')
@user_passes_test(is_staff_user, login_url='/admin-login/')
@require_POST
def asset_delete(request, asset_id):
    asset = get_object_or_404(Asset, id=asset_id)
    asset.delete()
    return JsonResponse({'success': True})


@login_required(login_url='/admin-login/')
@user_passes_test(is_staff_user, login_url='/admin-login/')
def portfolio_upload_page(request):
    categories = Category.objects.all()
    portfolio_items = Portfolio.objects.all()[:24]
    return render(request, 'gallery/portfolio_upload.html', {
        'categories': categories,
        'portfolio_items': portfolio_items,
        'active_nav': 'portfolio',
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
        'edit_url': reverse('gallery:portfolio_edit', args=[item.id]),
    })


@login_required(login_url='/admin-login/')
@user_passes_test(is_staff_user, login_url='/admin-login/')
@require_POST
def portfolio_delete(request, item_id):
    item = get_object_or_404(Portfolio, id=item_id)
    item.delete()
    return JsonResponse({'success': True})


@login_required(login_url='/admin-login/')
@user_passes_test(is_staff_user, login_url='/admin-login/')
def portfolio_edit(request, item_id):
    item = get_object_or_404(Portfolio, id=item_id)
    categories = Category.objects.all()
    all_tags = Tag.objects.all()

    if request.method == 'POST':
        item.title = request.POST.get('title', '').strip()
        item.description = request.POST.get('description', '').strip()
        item.category_id = request.POST.get('category') or None
        item.order = request.POST.get('order') or 0
        item.save()
        item.tags.set(request.POST.getlist('tags'))

        messages.success(request, 'Portfolio item updated.')
        return redirect('gallery:portfolio_upload_page')

    return render(request, 'gallery/portfolio_edit.html', {
        'item': item,
        'categories': categories,
        'all_tags': all_tags,
        'active_nav': 'portfolio',
    })


@login_required(login_url='/admin-login/')
@user_passes_test(is_staff_user, login_url='/admin-login/')
def manage_categories(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, 'Category name is required.')
        else:
            try:
                Category.objects.create(name=name)
                messages.success(request, 'Category added.')
            except IntegrityError:
                messages.error(request, f'A category named "{name}" already exists.')
        return redirect('gallery:manage_categories')

    categories = Category.objects.all()
    return render(request, 'gallery/manage_categories.html', {
        'categories': categories,
        'active_nav': 'categories',
    })


@login_required(login_url='/admin-login/')
@user_passes_test(is_staff_user, login_url='/admin-login/')
def category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        category.name = request.POST.get('name', '').strip()
        try:
            category.save()
            messages.success(request, 'Category updated.')
            return redirect('gallery:manage_categories')
        except IntegrityError:
            messages.error(request, f'A category named "{category.name}" already exists.')

    return render(request, 'gallery/category_edit.html', {
        'category': category,
        'active_nav': 'categories',
    })


@login_required(login_url='/admin-login/')
@user_passes_test(is_staff_user, login_url='/admin-login/')
@require_POST
def category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    messages.success(request, 'Category deleted.')
    return redirect('gallery:manage_categories')


@login_required(login_url='/admin-login/')
@user_passes_test(is_staff_user, login_url='/admin-login/')
def manage_tags(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, 'Tag name is required.')
        else:
            try:
                Tag.objects.create(name=name)
                messages.success(request, 'Tag added.')
            except IntegrityError:
                messages.error(request, f'A tag named "{name}" already exists.')
        return redirect('gallery:manage_tags')

    tags = Tag.objects.all()
    return render(request, 'gallery/manage_tags.html', {
        'tags': tags,
        'active_nav': 'tags',
    })


@login_required(login_url='/admin-login/')
@user_passes_test(is_staff_user, login_url='/admin-login/')
def tag_edit(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)

    if request.method == 'POST':
        tag.name = request.POST.get('name', '').strip()
        try:
            tag.save()
            messages.success(request, 'Tag updated.')
            return redirect('gallery:manage_tags')
        except IntegrityError:
            messages.error(request, f'A tag named "{tag.name}" already exists.')

    return render(request, 'gallery/tag_edit.html', {
        'tag': tag,
        'active_nav': 'tags',
    })


@login_required(login_url='/admin-login/')
@user_passes_test(is_staff_user, login_url='/admin-login/')
@require_POST
def tag_delete(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    tag.delete()
    messages.success(request, 'Tag deleted.')
    return redirect('gallery:manage_tags')
