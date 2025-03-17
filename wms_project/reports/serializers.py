from rest_framework import serializers
from .models import Report, ReportSchedule, ReportTemplate, GeneratedReport
from django.contrib.auth.models import User
from warehouse.serializers import WarehouseSerializer

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class ReportSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)
    warehouses = WarehouseSerializer(many=True, read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    format_display = serializers.CharField(source='get_format_display', read_only=True)
    
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'file']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        
        warehouse_ids = self.context['request'].data.get('warehouse_ids', [])
        report = Report.objects.create(**validated_data)
        
        if warehouse_ids:
            report.warehouses.set(warehouse_ids)
            
        return report


class ReportScheduleSerializer(serializers.ModelSerializer):
    report = ReportSerializer(read_only=True)
    report_id = serializers.PrimaryKeyRelatedField(
        queryset=Report.objects.all(), 
        source='report', 
        write_only=True
    )
    recipients = UserSimpleSerializer(many=True, read_only=True)
    recipient_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='recipients',
        write_only=True,
        many=True,
        required=False
    )
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    
    class Meta:
        model = ReportSchedule
        fields = '__all__'
        read_only_fields = ['next_run', 'last_run']
    
    def create(self, validated_data):
        recipients = validated_data.pop('recipients', [])
        schedule = ReportSchedule.objects.create(**validated_data)
        
        if recipients:
            schedule.recipients.set(recipients)
            
        return schedule


class ReportTemplateSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    
    class Meta:
        model = ReportTemplate
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return ReportTemplate.objects.create(**validated_data)


class GeneratedReportSerializer(serializers.ModelSerializer):
    report = ReportSerializer(read_only=True)
    report_id = serializers.PrimaryKeyRelatedField(
        queryset=Report.objects.all(), 
        source='report', 
        write_only=True
    )
    generated_by = UserSimpleSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = GeneratedReport
        fields = '__all__'
        read_only_fields = ['generated_by', 'status', 'start_time', 'end_time', 'file', 'error_message']
    
    def create(self, validated_data):
        validated_data['generated_by'] = self.context['request'].user
        validated_data['status'] = 'PENDING'
        return GeneratedReport.objects.create(**validated_data)