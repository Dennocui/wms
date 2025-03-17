from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'suppliers', views.SupplierViewSet)
router.register(r'customers', views.CustomerViewSet)
router.register(r'purchase-orders', views.PurchaseOrderViewSet)
router.register(r'purchase-order-items', views.PurchaseOrderItemViewSet)
router.register(r'sales-orders', views.SalesOrderViewSet)
router.register(r'sales-order-items', views.SalesOrderItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]