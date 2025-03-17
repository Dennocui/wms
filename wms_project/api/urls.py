from django.urls import path, include

urlpatterns = [
    path('inventory/', include('inventory.urls')),
    path('warehouse/', include('warehouse.urls')),
    path('orders/', include('orders.urls')),
    path('users/', include('users.urls')),
    path('reports/', include('reports.urls')),
]