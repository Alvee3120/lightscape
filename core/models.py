from django.db import models


class ServicePlan(models.Model):
    class Unit(models.TextChoices):
        DAY = 'day', 'Day'
        EVENT = 'event', 'Event'
        PROJECT = 'project', 'Project'

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_prefix = models.CharField(max_length=20, blank=True, help_text='e.g. "From" for starting-at pricing')
    unit = models.CharField(max_length=10, choices=Unit.choices, default=Unit.DAY)
    is_featured = models.BooleanField(default=False, help_text='Highlights this card, e.g. "Most booked"')
    badge_text = models.CharField(max_length=50, blank=True, default='Most booked')
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers show first")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name

    @property
    def display_price(self):
        whole = self.price.to_integral_value()
        if self.price == whole:
            return f"{whole:,.0f}"
        return f"{self.price:,.2f}"


class ServicePlanFeature(models.Model):
    plan = models.ForeignKey(ServicePlan, related_name='features', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.text


class SiteContent(models.Model):
    heading = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    button_text = models.CharField(max_length=50, blank=True)
    button_url = models.CharField(max_length=200, blank=True)
    hero_image = models.ImageField(upload_to='site_content/', blank=True, null=True)

    class Meta:
        verbose_name = "About Page Content"
        verbose_name_plural = "About Page Content"

    def __str__(self):
        return self.heading


class ContactInfo(models.Model):
    studio_location = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)

    class Meta:
        verbose_name = "Contact Info"
        verbose_name_plural = "Contact Info"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    def __str__(self):
        return "Contact Info"
