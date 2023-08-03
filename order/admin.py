from django.contrib import admin
from .models import Order, OrderItem

# Register your models here.


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "buyer",
        "shipping_address",
        "created_at",
        "status",
        "delivery_status",
    )
    list_filter = (
        "status",
        "delivery_status",
        "created_at",
        "updated_at",
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "product",
        "quantity",
        "created_at",
    )
    list_filter = ("created_at",)
