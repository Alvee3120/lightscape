from django.contrib import admin
from .models import SiteContent, ServicePlan, ServicePlanFeature, ContactInfo


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ('heading', 'button_text')


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('studio_location', 'email', 'phone')

    def has_add_permission(self, request):
        return not ContactInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class ServicePlanFeatureInline(admin.TabularInline):
    model = ServicePlanFeature
    extra = 1


@admin.register(ServicePlan)
class ServicePlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'unit', 'is_featured', 'order')
    inlines = [ServicePlanFeatureInline]
