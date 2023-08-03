from django.contrib import admin
from .models import Feedback, SalesProduct, FeaturedProduct, CompanySocials, DealsBanner


# Register your models here.
@admin.register(SalesProduct)
class SalesProductAdmin(admin.ModelAdmin):
    list_display = ("short_name", "brand", "compatibility", "price")
    list_filter = (
        "category",
        "subcategory",
    )
    search_fields = ("short_name", "brand__startswith")


@admin.register(FeaturedProduct)
class FeaturedProductAdmin(admin.ModelAdmin):
    pass
    list_display = ("short_name", "brand", "compatibility", "price")
    list_filter = (
        "category",
        "subcategory",
    )
    search_fields = ("short_name", "brand__startswith")


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone_number")
    list_filter = ("created_at",)


@admin.register(CompanySocials)
class CompanySocialAccountAdmin(admin.ModelAdmin):
    pass


@admin.register(DealsBanner)
class DealsBannerAdmin(admin.ModelAdmin):
    pass
