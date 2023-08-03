# from attr import field
from rest_framework.serializers import ModelSerializer

from order.serializers import OrderSerializer
from .models import User, Profile, Garage, Vehicle, Address
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "mobile_number"]


class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ["token", "username", "email", "first_name", "last_name", "mobile_number", "address"]

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"


class GarageSerializer(ModelSerializer):
    vehicle = serializers.DictField(source="get_vehicle", read_only=True)

    class Meta:
        model = Garage
        fields = ['id', 'vehicle']


class VehicleSerializer(ModelSerializer):
    class Meta:
        model = Vehicle
        fields = "__all__"


class AddressSerializer(ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"