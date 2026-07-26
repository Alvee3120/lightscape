import uuid
from datetime import timedelta
from django.db import models
from django.utils import timezone
from gallery.models import Asset


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        FAILED = 'failed', 'Failed'
        CANCELLED = 'cancelled', 'Cancelled'

    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField()

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    amount_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Stripe references — filled in once checkout session is created / confirmed
    gateway_session_id = models.CharField(max_length=255, blank=True, null=True)  # SSLCommerz sessionkey
    gateway_transaction_id = models.CharField(max_length=255, blank=True, null=True)  # SSLCommerz tran_id / val_id

    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {str(self.order_id)[:8]} - {self.email} - {self.status}"

    def mark_paid(self):
        self.status = self.Status.PAID
        self.paid_at = timezone.now()
        self.save(update_fields=['status', 'paid_at', 'gateway_transaction_id'])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name='order_items')

    # Price locked at the moment of purchase (protects against later price changes)
    price_at_purchase = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.asset.title} in Order {str(self.order.order_id)[:8]}"


class DownloadToken(models.Model):
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='download_tokens')

    # Null order = this was a FREE download, not tied to a purchase
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='download_tokens', blank=True, null=True)

    max_uses = models.PositiveIntegerField(default=3)
    use_count = models.PositiveIntegerField(default=0)

    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    is_revoked = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=48)
        super().save(*args, **kwargs)

    def is_valid(self):
        if self.is_revoked:
            return False
        if timezone.now() > self.expires_at:
            return False
        if self.use_count >= self.max_uses:
            return False
        return True

    def register_use(self):
        self.use_count += 1
        self.save(update_fields=['use_count'])
        # Also bump the asset's overall download counter for analytics
        self.asset.download_count += 1
        self.asset.save(update_fields=['download_count'])

    def __str__(self):
        return f"Token for {self.asset.title} ({'valid' if self.is_valid() else 'invalid'})"