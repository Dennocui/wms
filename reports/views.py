from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import Report, ReportSchedule, ReportTemplate, GeneratedReport
from .serializers import (
    ReportSerializer, 
    ReportScheduleSerializer, 
    ReportTemplateSerializer, 
    GeneratedReportSerializer
)
from .permissions import IsAdminOrManager, IsOwnerOrAdmin
from .report_generators import generate_report
import csv
import io
import json
from datetime import datetime, timedelta


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'report_type']
    ordering_fields = ['title', 'created_at', 'report_type']
    
    def get_queryset(self):
        user = self.request.user
        queryset = Report.objects.all()
        
        # Filter by warehouse if specified
        warehouse_id = self.request.query_params.get('warehouse_id', None)
        if warehouse_id:
            queryset = queryset.filter(warehouses__id=warehouse_id)
        
        # Filter by report type if specified
        report_type = self.request.query_params.get('report_type', None)
        if report_type:
            queryset = queryset.filter(report_type=report_type)
            
        # Admin can see all reports
        if user.profile.role == 'ADMIN':
            return queryset
            
        # Managers can see reports for their warehouses or created by them
        if user.profile.role == 'MANAGER':
            return queryset.filter(
                Q(warehouses__in=user.profile.warehouses.all()) | 
                Q(created_by=user) |
                Q(is_public=True)
            ).distinct()
            
        # Others can only see their reports or public reports
        return queryset.filter(
            Q(created_by=user) | 
            Q(is_public=True)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        report = self.get_object()
        
        # Use parameters from request if provided, otherwise use report defaults
        parameters = request.data.get('parameters', report.parameters)
        
        # Create a new generated report
        generated_report = GeneratedReport.objects.create(
            report=report,
            generated_by=request.user,
            status='PROCESSING',
            parameters_used=parameters
        )
        
        # Start the report generation process
        # In a real application, this would typically be done asynchronously
        try:
            generate_report(generated_report)
            return Response(
                GeneratedReportSerializer(generated_report).data,
                status=status.HTTP_202_ACCEPTED
            )
        except Exception as e:
            generated_report.status = 'FAILED'
            generated_report.error_message = str(e)
            generated_report.save()
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        report = self.get_object()
        
        # Check if there's a generated report
        generated_report_id = request.query_params.get('generated_report_id', None)
        if generated_report_id:
            try:
                generated_report = GeneratedReport.objects.get(id=generated_report_id, report=report)
                if generated_report.file:
                    # Serve the file
                    response = HttpResponse(
                        generated_report.file,
                        content_type='application/octet-stream'
                    )
                    response['Content-Disposition'] = f'attachment; filename="{report.title}_{generated_report.start_time.strftime("%Y%m%d_%H%M%S")}.{report.format.lower()}"'
                    return response
                else:
                    return Response(
                        {'error': 'Report file not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            except GeneratedReport.DoesNotExist:
                return Response(
                    {'error': 'Generated report not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            return Response(
                {'error': 'Generated report ID not provided'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ReportScheduleViewSet(viewsets.ModelViewSet):
    queryset = ReportSchedule.objects.all()
    serializer_class = ReportScheduleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrManager]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['report__title', 'frequency']
    ordering_fields = ['frequency', 'next_run', 'last_run']
    
    def get_queryset(self):
        user = self.request.user
        queryset = ReportSchedule.objects.all()
        
        # Filter by report if specified
        report_id = self.request.query_params.get('report_id', None)
        if report_id:
            queryset = queryset.filter(report_id=report_id)
        
        # Admin can see all schedules
        if user.profile.role == 'ADMIN':
            return queryset
            
        # Managers can see schedules for their warehouses or created by them
        if user.profile.role == 'MANAGER':
            return queryset.filter(
                Q(report__warehouses__in=user.profile.warehouses.all()) | 
                Q(report__created_by=user)
            ).distinct()
            
        # Others can only see their schedules
        return queryset.filter(report__created_by=user).distinct()
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        schedule = self.get_object()
        schedule.is_active = not schedule.is_active
        schedule.save()
        return Response(
            {'status': 'success', 'is_active': schedule.is_active},
            status=status.HTTP_200_OK
        )


class ReportTemplateViewSet(viewsets.ModelViewSet):
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'report_type']
    ordering_fields = ['name', 'created_at', 'report_type']
    
    def get_queryset(self):
        user = self.request.user
        queryset = ReportTemplate.objects.all()
        
        # Filter by report type if specified
        report_type = self.request.query_params.get('report_type', None)
        if report_type:
            queryset = queryset.filter(report_type=report_type)
            
        # Admin can see all templates
        if user.profile.role == 'ADMIN':
            return queryset
            
        # Others can see their templates or public templates
        return queryset.filter(
            Q(created_by=user) | 
            Q(is_public=True)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def create_report(self, request, pk=None):
        template = self.get_object()
        
        # Create a new report from the template
        report = Report.objects.create(
            title=f"Report from {template.name}",
            report_type=template.report_type,
            description=template.description,
            created_by=request.user,
            parameters=template.parameters,
            format=request.data.get('format', 'PDF'),
            is_public=False
        )
        
        # Set warehouses if provided
        warehouse_ids = request.data.get('warehouse_ids', [])
        if warehouse_ids:
            report.warehouses.set(warehouse_ids)
        
        return Response(
            ReportSerializer(report).data,
            status=status.HTTP_201_CREATED
        )


class GeneratedReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GeneratedReport.objects.all()
    serializer_class = GeneratedReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['report__title', 'status']
    ordering_fields = ['start_time', 'end_time', 'status']
    
    def get_queryset(self):
        user = self.request.user
        queryset = GeneratedReport.objects.all()
        
        # Filter by report if specified
        report_id = self.request.query_params.get('report_id', None)
        if report_id:
            queryset = queryset.filter(report_id=report_id)
        
        # Filter by status if specified
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        # Admin can see all generated reports
        if user.profile.role == 'ADMIN':
            return queryset
            
        # Managers can see generated reports for their warehouses or created by them
        if user.profile.role == 'MANAGER':
            return queryset.filter(
                Q(report__warehouses__in=user.profile.warehouses.all()) | 
                Q(report__created_by=user) |
                Q(generated_by=user)
            ).distinct()
            
        # Others can only see their generated reports
        return queryset.filter(
            Q(report__created_by=user) | 
            Q(generated_by=user)
        ).distinct()