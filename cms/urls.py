from django.urls import path
from . import views

app_name = 'cms'

urlpatterns = [
    path('export/', views.export, name='export'),
    path('product-bulk-upload/', views.product_bulk_upload, name='product-bulk-upload'),
    path('vehicle-bulk-upload/', views.vehicle_bulk_upload, name='vehicle-bulk-upload'),
    path('product-image-upload/', views.product_image_upload, name='product-image-upload'),
    path('post-feedback/', views.add_feedback, name='post-feedback'),
    path('get-sales-and-featured-product/', views.get_sales_and_featured_product, name='get-sales-and-featured-product'),
    path('get-company-social-links/', views.get_company_social_links, name='get-company-social-links'),
    path('get-deals-banner/', views.get_deals_banner, name='get-deals-banner'),
    path('export-delivered-orders/<str:order_status>/', views.ExportOrderView.as_view(), name='export_order'),
]