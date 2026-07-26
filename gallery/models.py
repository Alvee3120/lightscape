from django.db import models
from django.utils.text import slugify
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import generate_watermarked_preview




class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


    
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Asset(models.Model):
    # Unique public-facing identifier (safer than exposing DB id in URLs)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)

    tags = models.ManyToManyField(Tag, blank=True, related_name='assets')

    # Original full-resolution file — NEVER served directly to public
    original_file = models.ImageField(upload_to='originals/%Y/%m/')

    # Auto-generated watermarked/compressed preview — safe for public display
    preview_file = models.ImageField(upload_to='previews/%Y/%m/', blank=True, null=True)

    # Pricing
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    # Publishing control
    is_published = models.BooleanField(default=True)

    # Analytics
    download_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = f"{base_slug}-{str(self.uid)[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def is_paid(self):
        return not self.is_free

class Portfolio(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)

    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='portfolio_items'
    )

    original_file = models.ImageField(upload_to='portfolio/originals/%Y/%m/')
    preview_file = models.ImageField(upload_to='portfolio/previews/%Y/%m/', blank=True, null=True)

    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers show first")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name_plural = "Portfolio items"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = f"{base_slug}-{str(self.uid)[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


@receiver(post_save, sender=Portfolio)
def create_portfolio_preview_on_upload(sender, instance, created, **kwargs):
    if instance.original_file and not instance.preview_file:
        preview_content = generate_watermarked_preview(instance.original_file, watermark_opacity=45)
        filename = f"preview_{instance.slug}.jpg"
        instance.preview_file.save(filename, preview_content, save=False)
        instance.save(update_fields=['preview_file'])

@receiver(post_save, sender=Asset)
def create_preview_on_upload(sender, instance, created, **kwargs):
    # Only generate a preview if one doesn't exist yet (avoids infinite save loop)
    if instance.original_file and not instance.preview_file:
        preview_content = generate_watermarked_preview(instance.original_file)
        filename = f"preview_{instance.slug}.jpg"
        # save=True would re-trigger this signal, so we save the field manually then save the model without re-firing
        instance.preview_file.save(filename, preview_content, save=False)
        instance.save(update_fields=['preview_file'])