from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'report', views.ReportViewSet)
router.register(r'schedules', views.ReportScheduleViewSet)
router.register(r'templates', views.ReportTemplateViewSet)
router.register(r'generated', views.GeneratedReportViewSet)



urlpatterns = [
    path('', include(router.urls)),
]