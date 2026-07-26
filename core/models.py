from django.db import models


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
