from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.hashers import make_password
from .models import User, TempUser, Address
from .serializers import *
from utils import sms
from store.models import WishList
from order.models import Order, OrderItem
from order.serializers import OrderItemSerializer, OrderSerializer

import pyotp, jwt, datetime

# Create your views here.


@api_view(["GET"])

def home(request):
    endpoint = ["home/"]

    return Response(endpoint)


# CHECK IF IT'S A NEW USER OR IT ALREADY EXISTS
@api_view(["POST"])
def user_identifier(request):
    data = request.data
    username = data["username"]
    user_exist = False

    # checking for the user in the database
    user = User.objects.filter(username=username)

    if user:
        user_exist = 1
    else:
        user_exist = 0

    print(user_exist)

    return Response(user_exist)


# TOKEN RETURNER FOR AUTHENTICATION ONLY
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    # data = request.data
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password"].required = False

    def validate(self, attrs):
        attrs.update({"password": "cd8d8530-fb8b-44ac-935d-cf764e52deda"})
        data = super().validate(attrs)
        print("Confirmed")
        print(self.user.otp)
        serializer = UserSerializerWithToken(self.user).data

        print("got here")
        for k, v in serializer.items():
            data[k] = v
        if self.user.otp_verified:
            # genetating the OTP for the user
            print("and it also got here")
            totp = pyotp.TOTP("base32secret3232")
            otp = totp.now()[:4]

            # updating the OTP in the user model for security reasons (not to allow user verified for lifetime)
            self.user.otp = otp
            # resseting the OTP_Verification in the user model for security reasons (not to allow user verified for lifetime)
            self.user.otp_verified = False
            self.user.save()
            return data
        else:
            return 401


# LOGIN USER GOES HERE
@api_view(['POST'])
def signin(request):
    data = request.data
    email = data["email"]
    first_name = data['firstName']
    last_name = data['lastName']
    password = data["password"]
    

    user = User.objects.filter(email=email).first()

    if user is None:
        raise AuthenticationFailed("User not found!")

    if not user.check_password(password):
        raise AuthenticationFailed("Incorrect password!")

    payload = {
        "id": user.id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        "iat": datetime.datetime.utcnow(),
    }

    token = jwt.encode(payload, "secret", algorithm="HS256") # generates access token for login
    serializer = UserSerializer(user)

    response = Response()

    response.set_cookie(key="jwt", value=token, httponly=True) # creates cookies for user session
    response.data = {"tokens": user.tokens(), "data":serializer.data}
    return response




# class TokenObtainPairView(TokenObtainPairView):
#     serializer_class = MyTokenObtainPairSerializer


# REGISTER USER GOES HERE
@api_view(["POST"])
def registerUser(request):
    trim_whitespace = lambda x: x.replace(" ", "")

    data = request.data

    trimmed_username = trim_whitespace(data["username"])
    first_name = trim_whitespace(data["firstName"])
    last_name = trim_whitespace(data["lastName"])
    password = data['password']
    phone_number = trim_whitespace(request.data.get("phoneNumber", ""))
    address = request.data.get('address', "")
    
    
    # genetating the OTP for the NEW USER
    

    user = User.objects.create(
        username=trimmed_username,
        first_name=first_name,
        last_name=last_name,
        email=trimmed_username,
        mobile_number=phone_number,
        password=make_password(password),
        address=address
    )

    user = User.objects.get(username=trimmed_username)

    serializers = UserSerializerWithToken(user, many=False)

    return Response(serializers.data)


# OTP SENDINDER
@api_view(["POST"])
def otp_sender(request):
    # genetating the OTP for the user
    totp = pyotp.TOTP("base32secret3232")
    otp = totp.now().lstrip("0")[:6].zfill(6)

    # getting the data
    data = request.data
    already_registered_user = bool(int(data["alreadyRegisteredUser"]))
    print(already_registered_user)

    # checking if the user IS REGISTERED ALREADY
    if already_registered_user:
        # cleaning up the username data
        username = data["username"].replace(" ", "")
        # updating the OTP in the user model
        user = User.objects.filter(username=username)
        user.update(otp=otp)
        # getting user mobile number to send OTP to it
        user_email = User.objects.get(username=username).email
        send_user_otp = sms.send_otp(user_email, otp)

        # checking if the OTP is successfully sent
        if send_user_otp["status"]:
            user.update(sent=timezone.now())
            return Response(
                {
                    "details": f"OTP sent to {user_email}"
                }
            )
        else:
            return Response(send_otp)
    else:
        user_phone_number = data["phoneNumber"].replace(" ", "")
        # deleteing previous TMP user table if it exists
        TempUser.objects.filter(phone_number=user_phone_number).delete()
        # creating new OTP for temporary USER that's just registering
        TempUser.objects.create(phone_number=user_phone_number, otp=otp)
        send_otp = sms.send_otp(user_phone_number, otp)

        # checking if the OTP is successfully sent
        if send_otp["status"]:
            TempUser.objects.filter(phone_number=user_phone_number).update(
                sent=timezone.now()
            )
            return Response(
                {
                    "status": 1,
                    "masked_phone": f"{user_phone_number[0:5]}*****{user_phone_number[len(user_phone_number)-2:len(user_phone_number)]}",
                }
            )
        else:
            return Response(send_otp)


# VERIFY OTP
@api_view(["POST"])
def verify_otp(request):
    trim_whitespace = lambda x: x.replace(" ", "")
    data = request.data

    username = trim_whitespace(data["username"])
    enteredOtp = data["otp"]

    # checking if the user IS ALREADY REGISTERED
    if User.objects.filter(username=username):
        # updating the OTP in the user model
        valid_otp = User.objects.get(username=username).otp
        otp_expired = User.objects.get(username=username).is_otp_expired()

        # checking if OTP is valid and not expired
        if enteredOtp == str(valid_otp) and not otp_expired:
            User.objects.filter(username=username).update(otp_verified=True)
            return Response(1)
        else:
            return Response(0)

    else:
        # GETTING the TEMP OTP for temporary USER that's just registering
        valid_otp = TempUser.objects.get(
            phone_number=trim_whitespace(data["phoneNumber"])
        ).otp
        otp_expired = TempUser.objects.get(
            phone_number=trim_whitespace(data["phoneNumber"])
        ).is_otp_expired()

        # checking if OTP is valid and not expired
        if enteredOtp == str(valid_otp) and not otp_expired:
            # deleting the temporary USER from the DATABSE
            TempUser.objects.filter(
                phone_number=trim_whitespace(data["phoneNumber"])
            ).delete()
            # returning response
            return Response(1)
        else:
            return Response(0)


# GET USER PROFILE
@api_view(["POST"])
def get_user_profile(request):
    user = User.objects.get(username = request.data['email'])
    # getting the user
    

    # checking the user type for serializing the data
    profile = Profile.objects.get(user=user)
    wishlist_count = WishList.objects.filter(user=user).count()
    order = Order.objects.filter(buyer=user, status="P")
    
    cart_items = OrderItem.objects.filter(order__buyer = user)

    serializer = {
        "user": UserSerializer(user, many=False).data,
        "profile": ProfileSerializer(profile, many=False).data,
        "wishlist_count": wishlist_count,
        "order": OrderSerializer(order, many=True).data,
        "cart_items": OrderItemSerializer(cart_items, many=True).data,
    }
    

    return Response(serializer)


# GET USER GARAGE
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_garage(request):
    # getting the user making the request
    user = request.user

    # serializing the data
    data = Garage.objects.filter(user=user)
    serialized_vehicles = GarageSerializer(data, many=True).data

    return Response(serialized_vehicles)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_user_garage(request):
    year = request.data["year"]
    make = request.data["make"].title()
    model = request.data["model"].title()

    vehicle, created = Vehicle.objects.get_or_create(year=year, make=make, model=model)

    try:
        garage, created = Garage.objects.get_or_create(
            user=request.user, vehicle=vehicle
        )
        return Response(status=status.HTTP_201_CREATED)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_from_user_garage(request, garage_id):
    try:
        garage = Garage.objects.get(user=request.user, id=garage_id)
    except Garage.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    garage.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# GET VEHICLES WHICH PARTS ARE AVAILABLE
@api_view(["GET"])
def get_vehicles(request):
    # serializing the data
    data = Vehicle.objects.all()
    serializer = VehicleSerializer(data, many=True)

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    user = request.user

    # Retrieve data from the request
    first_name = request.data.get("firstName", user.first_name)
    last_name = request.data.get("lastName", user.last_name)
    email = request.data.get("email", user.email)
    phone_number = request.data.get("phoneNumber", user.mobile_number)

    # Validate the data
    if not first_name and not last_name and not email and not phone_number:
        return Response(
            {"error": "At least one field must be provided"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Update the user's profile
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if email:
        user.email = email
    if phone_number:
        user.mobile_number = phone_number
    user.save()

    # Serialize and return the updated user
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_user_address(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    serializer = ProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
