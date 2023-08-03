from django.contrib import admin
from django.db import IntegrityError, transaction
from .models import User, Profile, TempUser, Vehicle, Garage, Address

# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "first_name", "last_name", "mobile_number")
    list_filter = ("date_joined",)
    search_fields = ("last_name__startswith",)


@admin.register(TempUser)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "address_type", "street_address", "postal_code", "country")


@admin.register(Profile)
class TempUserAdmin(admin.ModelAdmin):
    pass


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("make", "model", "year")

    list_filter = ("year", "make")
    search_fields = ("make", "model__startswith")

    # @transaction.non_atomic_requests
    def save_model(self, request, obj, form, change):
        try:
            with transaction.atomic():
                obj.save()
        except IntegrityError:
            form.add_error(None, "This vehicle already exists.")
        # return super().save_model(request, obj, form, change)


@admin.register(Garage)
class GarageAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "user")

    list_filter = ("vehicle",)
