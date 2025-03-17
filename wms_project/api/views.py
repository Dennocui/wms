from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'inventory': reverse('inventory-list', request=request, format=format),
        'warehouse': reverse('warehouse-list', request=request, format=format),
        'orders': reverse('order-list', request=request, format=format),
        'users': reverse('user-list', request=request, format=format),
        'reports': reverse('report-list', request=request, format=format),
    })