from django.contrib import admin
from .models import Report, ReportSchedule, ReportTemplate, GeneratedReport

class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'created_by', 'format', 'is_scheduled', 'is_public', 'created_at')
    list_filter = ('report_type', 'format', 'is_scheduled', 'is_public')
    search_fields = ('title', 'description', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('warehouses',)
    
    fieldsets = (
        ('Report Information', {
            'fields': ('title', 'report_type', 'description', 'created_by', 'warehouses')
        }),
        ('Output Options', {
            'fields': ('format', 'parameters', 'file')
        }),
        ('Settings', {
            'fields': ('is_scheduled', 'is_public', 'created_at', 'updated_at')
        }),
    )

class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ('report', 'frequency', 'next_run', 'last_run', 'is_active')
    list_filter = ('frequency', 'is_active')
    search_fields = ('report__title',)
    readonly_fields = ('next_run', 'last_run')
    filter_horizontal = ('recipients',)
    
    fieldsets = (
        ('Schedule Information', {
            'fields': ('report', 'frequency', 'time')
        }),
        ('Schedule Details', {
            'fields': ('day_of_week', 'day_of_month', 'next_run', 'last_run')
        }),
        ('Recipients', {
            'fields': ('recipients', 'email_addresses')
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
    )

class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'report_type', 'created_by', 'is_public', 'created_at')
    list_filter = ('report_type', 'is_public')
    search_fields = ('name', 'description', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'report_type', 'description', 'created_by')
        }),
        ('Parameters', {
            'fields': ('parameters',)
        }),
        ('Settings', {
            'fields': ('is_public', 'created_at', 'updated_at')
        }),
    )

class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ('report', 'generated_by', 'status', 'start_time', 'end_time')
    list_filter = ('status',)
    search_fields = ('report__title', 'generated_by__username')
    readonly_fields = ('start_time', 'end_time', 'error_message', 'parameters_used')
    
    fieldsets = (
        ('Report Information', {
            'fields': ('report', 'generated_by', 'status')
        }),
        ('Execution Details', {
            'fields': ('start_time', 'end_time', 'parameters_used')
        }),
        ('Output', {
            'fields': ('file', 'error_message')
        }),
    )

admin.site.register(Report, ReportAdmin)
admin.site.register(ReportSchedule, ReportScheduleAdmin)
admin.site.register(ReportTemplate, ReportTemplateAdmin)
admin.site.register(GeneratedReport, GeneratedReportAdmin)