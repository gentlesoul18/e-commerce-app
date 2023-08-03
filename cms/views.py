from pprint import pprint
import re
import csv
import cloudinary
import cloudinary.api
import cloudinary.uploader

from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from django.contrib.sites.shortcuts import get_current_site

from .forms import ProductImageUploadForm, UploadForm
from .models import (
    Feedback,
    SalesProduct,
    FeaturedProduct,
    CompanySocials,
    DealsBanner,
    UploadImage,
)
from .serializers import CompanySocialsSerializer, DealsBannerSerializer
from store.serializers import ProductDetailSerializer
from store.models import Product, Category, Subcategory
from account.models import User, Vehicle
from order.models import Order, OrderItem

# Create your views here.


class ExportOrderView(View):
    http_method_names = ["get"]
    model = OrderItem
    status = ""

    def get(self, request, *args, **kwargs):
        self.status = self.kwargs["order_status"]
        if self.status not in [
            Order.IN_PROGESS,
            Order.SHIPPED,
            Order.DELIVERED,
            Order.CANCELLED,
        ]:
            return HttpResponse("Invalid order status")

        response = HttpResponse(content_type="text/csv")
        response[
            "Content-Disposition"
        ] = f"attachment; filename={self.status}-orders.csv"
        writer = csv.writer(response)

        # Write headers
        writer.writerow(
            [
                "Product Name",
                "Product SKU",
                "Product Price",
                "Quantity",
                "Order Date",
                "Order Status",
            ]
        )

        # Get order items and associated product information
        order_items = OrderItem.objects.filter(
            order__delivery_status=self.status
        ).select_related("product")

        for item in order_items:
            writer.writerow(
                [
                    item.product.short_name,
                    item.product.sku,
                    item.product.price,
                    item.quantity,
                    item.order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    item.order.get_status_display(),
                ]
            )

        return response


@api_view(["POST"])
def add_feedback(request) -> Response:
    data = request.data

    Feedback.objects.create(
        name=data["name"],
        email=data["email"],
        phone_number=data["phoneNumber"],
        message=data["message"],
    )

    return Response(200)


@api_view(["GET"])
def get_sales_and_featured_product(request) -> Response:
    sales_product = SalesProduct.objects.all()
    featured_product = FeaturedProduct.objects.all()

    response = {
        "sales_product": ProductDetailSerializer(sales_product, many=True).data,
        "featured_product": ProductDetailSerializer(featured_product, many=True).data,
    }

    return Response(response)


def product_bulk_upload(request):
    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            decoded_file = file.read().decode("utf-8", errors="replace").splitlines()
            reader = csv.DictReader(decoded_file)

            for row in reader:
                global year, make, model
                year = 0
                make = ""
                model = ""
                # checking if there is specific vehicle
                try:
                    if row["Specific Vehicle"]:
                        value = row["Specific Vehicle"]

                        pattern = r"[^,]+"
                        matches = re.findall(pattern, value)
                        # print(matches)
                        try:
                            if matches:
                                # print(matches)
                                # print(vehicle_model_code)
                                product = Product(
                                    category=Category.objects.get(name=row["Category"]),
                                    subcategory=Subcategory.objects.get(
                                        name=row["Subcategory"]
                                    )
                                    if row["Subcategory"]
                                    else None,
                                    short_name=row["Short Name"],
                                    long_name=row["Long Name"],
                                    sku=row["SKU"],
                                    part_number=row["Part Number"],
                                    brand=row["Brand"],
                                    condition=row["Condition"],
                                    package_size=row["Package Size"],
                                    short_desc=row["Short Desc"],
                                    long_desc=row["Long Desc"],
                                    image1=row["Image1"],
                                    image2=row["Image2"],
                                    image3=row["Image3"],
                                    compatibility=row["Compatibility"],
                                    supplier_name1=row["Supplier Name1"],
                                    supplier_price1=row["Supplier Price1"] or 0.0,
                                    supplier_name2=row["Supplier Name2"],
                                    supplier_price2=row["Supplier Price2"] or 0.0,
                                    book_location=row["Book Location"],
                                    stock_location=row["Stock Location"],
                                    gtin=row["GTIN"],
                                    mpn=row["MPN"],
                                    google_product_category=row[
                                        "Google Product Category"
                                    ],
                                    seo_product_title=row["SEO Product Title"],
                                    installation_video=row["Installation Video"],
                                    installation_guide=row["Installation Guide"],
                                    warranty=row["Warranty"],
                                    features=row["Features"],
                                    in_stock=row["In Stock"],
                                    price=float(row["Price"]),
                                )
                                product.save()
                                for vehicle_model_code in matches:
                                    specific_vehicle_qs = Vehicle.objects.filter(
                                        model_code=vehicle_model_code.upper().replace(
                                            " ", ""
                                        )
                                    )
                                    for vehicle in specific_vehicle_qs:
                                        product.specific_vehicle.add(vehicle)
                        except KeyError:
                            return render(request, "error.html")
                    else:
                        try:
                            product = Product(
                                category=Category.objects.get(name=row["Category"]),
                                subcategory=Subcategory.objects.get(
                                    name=row["Subcategory"]
                                )
                                if row["Subcategory"]
                                else None,
                                name=row["Name"],
                                sku=row["SKU"],
                                part_number=row["Part Number"],
                                brand=row["Brand"],
                                condition=row["Condition"],
                                package_size=row["Package Size"],
                                desc=row["Desc"],
                                image1=row["Image1"],
                                image2=row["Image2"],
                                image3=row["Image3"],
                                compatibility=row["Compatibility"],
                                supplier_name1=row["Supplier Name1"],
                                supplier_price1=row["Supplier Price1"] or 0.0,
                                supplier_name2=row["Supplier Name2"],
                                supplier_price2=row["Supplier Price2"] or 0.0,
                                book_location=row["Book Location"],
                                stock_location=row["Stock Location"],
                                installation_video=row["Installation Video"],
                                installation_guide=row["Installation Guide"],
                                gtin=row["GTIN"],
                                mpn=row["MPN"],
                                google_product_category=row["Google Product Category"],
                                seo_product_title=row["SEO Product Title"],
                                warranty=row["Warranty"],
                                features=row["Features"],
                                in_stock=row["In Stock"],
                                price=row["Price"],
                            )
                            product.save()
                            pass
                        except KeyError:
                            return render(request, "error.html")
                except KeyError:
                    return render(request, "error.html")
            return render(request, "upload_complete.html")
    else:
        form = UploadForm()
    return render(request, "index.html", {"form": form})


def vehicle_bulk_upload(request):
    pattern = re.compile(r"(\d{4})\s*-\s*(\d{4})")

    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)

        if form.is_valid():
            file = request.FILES["file"]
            decoded_file = file.read().decode("utf-8").splitlines()
            reader = csv.DictReader(decoded_file)
            vehicles_to_create = []

            for row in reader:
                year = row["Year"]
                match = pattern.match(year)

                if match:
                    year1 = int(match.group(1))
                    year2 = int(match.group(2))

                    vehicles_to_create += [
                        Vehicle(
                            model_code=row["Model Code"].upper(),
                            year=_year,
                            make=row["Make"],
                            model=row["Model"],
                        )
                        for _year in range(year1, year2 + 1)
                    ]
                else:
                    vehicles_to_create.append(
                        Vehicle(
                            model_code=row["Model Code"],
                            year=year,
                            make=row["Make"],
                            model=row["Model"],
                        )
                    )

            # Use bulk_create to create multiple Vehicle objects at once
            Vehicle.objects.bulk_create(vehicles_to_create, ignore_conflicts=True)
            return render(request, "upload_complete.html")
    else:
        form = UploadForm()

    return render(request, "vehicle_bulk_upload.html", {"form": form})


def product_image_upload(request):
    image_url = UploadImage.objects.all()
    if request.method == "POST":
        form = ProductImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = request.FILES.getlist('images')
            images = []
            for image in image_file:
                response = cloudinary.uploader.upload(image)
                image_url = response["secure_url"]
                images.append(image_url)
                image = UploadImage(image=image_url)
                image.save()
            image_urls = UploadImage.objects.all()
            print(image_urls)
            context= {"form": form, "images": image_urls, "new_image": images}

            return render(request, "upload_image.html", context)
            
    else:
        
        form = ProductImageUploadForm()
        return render(request, "upload_image.html", {"form": form, "images": image_url})


@api_view(["GET"])
def get_company_social_links(request):
    social_links = CompanySocials.objects.all().first()

    serialized = CompanySocialsSerializer(social_links, many=False)

    return Response(serialized.data)


@api_view(["GET"])
def get_deals_banner(request):
    deals_banner = DealsBanner.objects.all()

    serialized = DealsBannerSerializer(deals_banner, many=True)

    return Response(serialized.data)


def export(request):
    return render(request, "export.html")
