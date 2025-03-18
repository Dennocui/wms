from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'user', views.UserViewSet)
router.register(r'profiles', views.UserProfileViewSet)
router.register(r'activities', views.ActivityViewSet)



urlpatterns = [
    path('', include(router.urls)),
]