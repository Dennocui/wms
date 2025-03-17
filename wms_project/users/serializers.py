from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Activity
from warehouse.serializers import WarehouseSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']
        read_only_fields = ['date_joined']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    warehouses = WarehouseSerializer(many=True, read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'role', 'role_display', 'warehouses', 'phone', 'address', 
                  'date_of_birth', 'profile_image', 'is_active', 'created_at', 'updated_at']

class UserProfileCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    warehouse_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role', 
                  'warehouse_ids', 'phone', 'address', 'date_of_birth', 'profile_image']
    
    def create(self, validated_data):
        warehouse_ids = validated_data.pop('warehouse_ids', [])
        user_data = {
            'username': validated_data.pop('username'),
            'email': validated_data.pop('email'),
            'password': validated_data.pop('password'),
            'first_name': validated_data.pop('first_name', ''),
            'last_name': validated_data.pop('last_name', ''),
        }
        
        user = User.objects.create_user(**user_data)
        profile = UserProfile.objects.create(user=user, **validated_data)
        
        if warehouse_ids:
            profile.warehouses.set(warehouse_ids)
        
        return profile

class ActivitySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = Activity
        fields = ['id', 'user', 'username', 'action', 'action_display', 'description', 
                  'model_name', 'object_id', 'ip_address', 'user_agent', 'timestamp']
        read_only_fields = ['timestamp']