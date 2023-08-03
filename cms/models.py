from django.db import models
from store.models import Product
from cloudinary.models import CloudinaryField
# Create your models here.


def banner_image_path(instance, filename):
    return f"banner/{instance.title}/{filename}"


class SalesProduct(Product):
    pass


class FeaturedProduct(Product):
    pass


class Feedback(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    message = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.name} {self.created_at}"


class CompanySocials(models.Model):
    facebook = models.URLField(verbose_name="Facebook", null=True, blank=True)
    twitter = models.URLField(verbose_name="Twitter", null=True, blank=True)
    instagram = models.URLField(verbose_name="Instagram", null=True, blank=True)
    youtube = models.URLField(verbose_name="Youtube", null=True, blank=True)
    linkedIn = models.URLField(verbose_name="LinkedIn", null=True, blank=True)
    whatsApp = models.URLField(
        verbose_name="WhatsApp", default=None, null=True, blank=True
    )

    class Meta:
        verbose_name_plural = "Company Social Accounts"

    def __str__(self) -> str:
        return "Company Social Accounts"


class DealsBanner(models.Model):
    COLOR_CHOICES = (
        ("orange", "orange"),
        ("black", "black"),
    )

    title = models.CharField(max_length=35)
    sub_title = models.CharField(max_length=70)
    category_tag = models.CharField(max_length=50, blank=False, null=False, default="Engine")
    text_color = models.CharField(
        max_length=10, choices=COLOR_CHOICES, default=COLOR_CHOICES[0]
    )
    image = models.ImageField(upload_to=banner_image_path, blank=True)

    def __str__(self) -> str:
        return f"{self.title}"

class UploadImage(models.Model):
    image = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.image