import datetime
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

from django.utils.translation import gettext as _

# Create your models here.


# User table
class User(AbstractUser):
    username = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=8, null=True)
    email = models.EmailField(max_length=255, null=True)
    mobile_number = models.CharField(max_length=15, null=True, default="null")
    address = models.CharField(max_length=255, null=True, blank=True, default="null")
    # otp = models.IntegerField(unique=True, blank=True, default=1000)
    # otp_verified = models.BooleanField(default=False)
    # sent = models.DateTimeField(null=True)

    USERNAME_FIELD = "username"

    def update_otp(self, otp):
        self.otp = otp

    def is_otp_expired(self):
        expiration_date = self.sent + datetime.timedelta(
            minutes=settings.TOKEN_EXPIRE_MINUTES
        )
        return expiration_date <= timezone.now()
 
    def __str__(self) -> str:
        return self.username


# Customer profile table
class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="consumer_profile"
    )
    street_address = models.CharField(max_length=255, blank=True, null=True)
    apt = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=255, blank=True, null=True)
    cashback = models.IntegerField(blank=True, null=True, default=24)

    def __str__(self) -> str:
        return f"{self.user} Profile"


# Temporary user table for verifying otp for un registered users
class TempUser(models.Model):
    phone_number = models.CharField(max_length=15)
    otp = models.IntegerField(blank=True)
    sent = models.DateTimeField(null=True)

    def is_otp_expired(self):
        expiration_date = self.sent + datetime.timedelta(
            minutes=settings.TOKEN_EXPIRE_MINUTES
        )
        return expiration_date <= timezone.now()

    def __str__(self):
        return self.phone_number


class Vehicle(models.Model):
    model_code = models.CharField(max_length=255, blank=True, null=True)
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    make = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.make = self.make.title()
        self.model = self.model.title()
        super(Vehicle, self).save(*args, **kwargs)

    class Meta:
        unique_together = ("year", "make", "model")

    def get_vehicle_name(self) -> str:
        return f"{self.year}-{self.make}-{self.model}"

    def __str__(self) -> str:
        return f"{self.year} {self.make} {self.model}"


# User vehicle garage model
class Garage(models.Model):
    user = models.ForeignKey(
        User, related_name="users_garage", on_delete=models.CASCADE
    )
    vehicle = models.ForeignKey(
        Vehicle,
        related_name="user_vehicles",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name_plural = "Garage"

    def get_vehicle(self) -> dict:
        return {
            "year": self.vehicle.year,
            "make": self.vehicle.make,
            "model": self.vehicle.model,
        }

    def __str__(self) -> str:
        return f"{self.vehicle.make} {self.vehicle.model} {self.vehicle.year} owned by {self.user}"


class Address(models.Model):
    # Address options
    BILLING = "B"
    SHIPPING = "S"

    ADDRESS_CHOICES = ((BILLING, _("billing")), (SHIPPING, _("shipping")))

    user = models.ForeignKey(User, related_name="addresses", on_delete=models.CASCADE)
    address_type = models.CharField(
        max_length=1, choices=ADDRESS_CHOICES, default=ADDRESS_CHOICES[1]
    )
    # default = models.BooleanField(default=False)
    apartment_address = models.CharField(max_length=255, blank=True, null=True)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True)
    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user.username} {self.street_address} {self.city} {self.country}"
