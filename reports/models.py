from django.db import models
from django.contrib.auth.models import User
from warehouse.models import Warehouse

class Report(models.Model):
    REPORT_TYPES = (
        ('INVENTORY', 'Inventory Report'),
        ('ORDER', 'Order Report'),
        ('SHIPPING', 'Shipping Report'),
        ('RECEIVING', 'Receiving Report'),
        ('USER_ACTIVITY', 'User Activity Report'),
        ('PERFORMANCE', 'Performance Report'),
        ('SALES', 'Sales Report'),
        ('CUSTOM', 'Custom Report'),
    )
    
    FORMAT_CHOICES = (
        ('PDF', 'PDF'),
        ('CSV', 'CSV'),
        ('EXCEL', 'Excel'),
        ('JSON', 'JSON'),
    )
    
    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parameters = models.JSONField(blank=True, null=True)  # Stored as JSON
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='PDF')
    file = models.FileField(upload_to='reports/', blank=True, null=True)
    is_scheduled = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    warehouses = models.ManyToManyField(Warehouse, related_name='reports', blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.get_report_type_display()}"
    
    class Meta:
        ordering = ['-created_at']


class ReportSchedule(models.Model):
    FREQUENCY_CHOICES = (
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
    )
    
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name='schedule')
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    day_of_week = models.IntegerField(blank=True, null=True)  # 0-6, where 0 is Monday
    day_of_month = models.IntegerField(blank=True, null=True)  # 1-31
    time = models.TimeField()
    next_run = models.DateTimeField()
    last_run = models.DateTimeField(blank=True, null=True)
    recipients = models.ManyToManyField(User, related_name='subscribed_reports', blank=True)
    email_addresses = models.TextField(blank=True, null=True)  # Additional email addresses, comma-separated
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.report.title} - {self.get_frequency_display()}"


class ReportTemplate(models.Model):
    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=20, choices=Report.REPORT_TYPES)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parameters = models.JSONField()  # Default parameters as JSON
    is_public = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.get_report_type_display()}"
    
    class Meta:
        ordering = ['name']


class GeneratedReport(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    )
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='generated_reports')
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    file = models.FileField(upload_to='reports/generated/', blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    parameters_used = models.JSONField(blank=True, null=True)  # Parameters used for this specific generation
    
    def __str__(self):
        return f"{self.report.title} - {self.start_time}"
    
    class Meta:
        ordering = ['-start_time']