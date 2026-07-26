from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import EmailMessage
from django.db.models import Sum
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from orders.models import Order
from gallery.models import Asset, Portfolio, Category
from .models import SiteContent, ServicePlan, ServicePlanFeature, ContactInfo

HOME_PREVIEW_LIMIT = 8


def home(request):
    hero_item = Portfolio.objects.filter(is_published=True).exclude(preview_file='').first()

    context = {
        'hero_item': hero_item,
        'categories': Category.objects.all(),
    }
    return render(request, 'core/home.html', context)


def home_storefront_filter(request):
    pricing = request.GET.get('pricing')
    assets = Asset.objects.filter(is_published=True)

    if pricing == 'free':
        assets = assets.filter(is_free=True)
    elif pricing == 'paid':
        assets = assets.filter(is_free=False)

    context = {
        'assets': assets[:HOME_PREVIEW_LIMIT],
        'active_pricing': pricing,
    }
    return render(request, 'core/_home_storefront_grid.html', context)


def home_portfolio_filter(request):
    category_slug = request.GET.get('category')
    items = Portfolio.objects.filter(is_published=True)

    if category_slug:
        items = items.filter(category__slug=category_slug)

    context = {
        'portfolio_items': items[:HOME_PREVIEW_LIMIT],
        'categories': Category.objects.all(),
        'active_category': category_slug,
    }
    return render(request, 'core/_home_portfolio_grid.html', context)


def about(request):
    content = SiteContent.objects.first()
    award_image = Portfolio.objects.filter(is_published=True).exclude(preview_file='').first()
    return render(request, 'core/about.html', {'content': content, 'award_image': award_image})


def service(request):
    hero_item = Portfolio.objects.filter(is_published=True).exclude(preview_file='').first()
    plans = ServicePlan.objects.prefetch_related('features').all()
    return render(request, 'core/service.html', {'hero_item': hero_item, 'plans': plans})


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and message:
            enquiry = EmailMessage(
                subject=f'New enquiry from {name}',
                body=f'From: {name} <{email}>\n\n{message}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.CONTACT_RECIPIENT_EMAIL],
                reply_to=[email],
            )
            try:
                enquiry.send(fail_silently=False)
            except Exception:
                messages.error(
                    request,
                    "Something went wrong sending your message. Please email "
                    "hello@lumenatlas.studio directly."
                )
            else:
                messages.success(
                    request,
                    "Thanks — your message has been sent. Expect a reply within two business days."
                )
            return redirect('contact')

        messages.error(request, 'Please fill in your name, email and message.')

    contact_info = ContactInfo.objects.first()
    return render(request, 'core/contact.html', {'contact_info': contact_info})


def is_staff_user(user):
    return user.is_staff


@login_required(login_url='/admin-login/')
@user_passes_test(is_staff_user, login_url='/admin-login/')
def admin_dashboard(request):
    # Overview stats
    total_revenue = Order.objects.filter(status=Order.Status.PAID).aggregate(
        total=Sum('amount_total')
    )['total'] or 0

    total_paid_orders = Order.objects.filter(status=Order.Status.PAID).count()

    total_free_downloads = Asset.objects.filter(is_free=True).aggregate(
        total=Sum('download_count')
    )['total'] or 0

    total_paid_downloads = Asset.objects.filter(is_free=False).aggregate(
        total=Sum('download_count')
    )['total'] or 0

    recent_orders = Order.objects.filter(status=Order.Status.PAID).order_by('-paid_at')[:20]
    top_assets = Asset.objects.order_by('-download_count')[:10]

    context = {
        'total_revenue': total_revenue,
        'total_paid_orders': total_paid_orders,
        'total_free_downloads': total_free_downloads,
        'total_paid_downloads': total_paid_downloads,
        'recent_orders': recent_orders,
        'top_assets': top_assets,
        'active_nav': 'overview',
    }
    return render(request, 'core/admin_dashboard.html', context)


@login_required(login_url='/admin-login/')
@user_passes_test(is_staff_user, login_url='/admin-login/')
def manage_content(request):
    content = SiteContent.objects.first()

    if request.method == 'POST':
        content.heading = request.POST.get('heading', '')
        content.description = request.POST.get('description', '')
        content.button_text = request.POST.get('button_text', '')
        content.button_url = request.POST.get('button_url', '')
        if request.FILES.get('hero_image'):
            content.hero_image = request.FILES['hero_image']
        content.save()
        messages.success(request, 'Site content updated.')
        return redirect('manage_content')

    return render(request, 'core/manage_content.html', {'content': content, 'active_nav': 'about'})


@login_required(login_url='/admin-login/')
@user_passes_test(is_staff_user, login_url='/admin-login/')
def manage_contact_info(request):
    info, _ = ContactInfo.objects.get_or_create(pk=1)

    if request.method == 'POST':
        info.studio_location = request.POST.get('studio_location', '').strip()
        info.email = request.POST.get('email', '').strip()
        info.phone = request.POST.get('phone', '').strip()
        info.save()
        messages.success(request, 'Contact info updated.')
        return redirect('manage_contact_info')

    return render(request, 'core/manage_contact_info.html', {'info': info, 'active_nav': 'contact'})


@login_required(login_url='/admin-login/')
@user_passes_test(is_staff_user, login_url='/admin-login/')
def manage_services(request):
    plans = ServicePlan.objects.prefetch_related('features').all()
    return render(request, 'core/manage_services.html', {'plans': plans, 'active_nav': 'services'})


@login_required(login_url='/admin-login/')
@user_passes_test(is_staff_user, login_url='/admin-login/')
@require_POST
def service_plan_create(request):
    name = request.POST.get('name', '').strip()
    price_raw = request.POST.get('price', '').strip()

    if not name or not price_raw:
        return JsonResponse({'error': 'Name and price are required'}, status=400)

    try:
        price = Decimal(price_raw)
    except InvalidOperation:
        return JsonResponse({'error': 'Price must be a valid number'}, status=400)

    plan = ServicePlan.objects.create(
        name=name,
        price=price,
        price_prefix=request.POST.get('price_prefix', '').strip(),
        unit=request.POST.get('unit') or ServicePlan.Unit.DAY,
        is_featured=request.POST.get('is_featured') == 'on',
        badge_text=request.POST.get('badge_text', '').strip() or 'Most booked',
        order=request.POST.get('order') or 0,
    )

    feature_lines = [f.strip() for f in request.POST.getlist('features[]') if f.strip()]
    ServicePlanFeature.objects.bulk_create([
        ServicePlanFeature(plan=plan, text=text, order=i)
        for i, text in enumerate(feature_lines)
    ])

    return JsonResponse({
        'success': True,
        'id': plan.id,
        'name': plan.name,
        'display_price': plan.display_price,
        'price_prefix': plan.price_prefix,
        'unit': plan.get_unit_display(),
        'is_featured': plan.is_featured,
        'badge_text': plan.badge_text,
        'order': plan.order,
        'features': feature_lines,
        'edit_url': reverse('service_plan_edit', args=[plan.id]),
    })


@login_required(login_url='/admin-login/')
@user_passes_test(is_staff_user, login_url='/admin-login/')
@require_POST
def service_plan_delete(request, plan_id):
    plan = get_object_or_404(ServicePlan, id=plan_id)
    plan.delete()
    return JsonResponse({'success': True})


@login_required(login_url='/admin-login/')
@user_passes_test(is_staff_user, login_url='/admin-login/')
def service_plan_edit(request, plan_id):
    plan = get_object_or_404(ServicePlan, id=plan_id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        price_raw = request.POST.get('price', '').strip()

        if not name or not price_raw:
            messages.error(request, 'Name and price are required.')
            return render(request, 'core/service_plan_edit.html', {'plan': plan, 'active_nav': 'services'})

        try:
            price = Decimal(price_raw)
        except InvalidOperation:
            messages.error(request, 'Price must be a valid number.')
            return render(request, 'core/service_plan_edit.html', {'plan': plan, 'active_nav': 'services'})

        plan.name = name
        plan.price = price
        plan.price_prefix = request.POST.get('price_prefix', '').strip()
        plan.unit = request.POST.get('unit') or ServicePlan.Unit.DAY
        plan.is_featured = request.POST.get('is_featured') == 'on'
        plan.badge_text = request.POST.get('badge_text', '').strip() or 'Most booked'
        plan.order = request.POST.get('order') or 0
        plan.save()

        feature_lines = [f.strip() for f in request.POST.getlist('features[]') if f.strip()]
        plan.features.all().delete()
        ServicePlanFeature.objects.bulk_create([
            ServicePlanFeature(plan=plan, text=text, order=i)
            for i, text in enumerate(feature_lines)
        ])

        messages.success(request, 'Service plan updated.')
        return redirect('manage_services')

    return render(request, 'core/service_plan_edit.html', {'plan': plan, 'active_nav': 'services'})