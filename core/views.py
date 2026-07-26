from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import EmailMessage
from django.db.models import Sum
from django.conf import settings
from orders.models import Order
from gallery.models import Asset, Portfolio, Category
from .models import SiteContent

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
    return render(request, 'core/service.html', {'hero_item': hero_item})


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

    return render(request, 'core/contact.html')


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
        return redirect('manage_content')

    return render(request, 'core/manage_content.html', {'content': content})