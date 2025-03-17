from django.db import models
from django.contrib.auth.models import User
from warehouse.models import Warehouse

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('ADMIN', 'Administrator'),
        ('MANAGER', 'Warehouse Manager'),
        ('SUPERVISOR', 'Supervisor'),
        ('STAFF', 'Staff'),
        ('PICKER', 'Picker'),
        ('PACKER', 'Packer'),
        ('RECEIVING', 'Receiving'),
        ('SHIPPING', 'Shipping'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STAFF')
    warehouses = models.ManyToManyField(Warehouse, related_name='assigned_users', blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

class Activity(models.Model):
    ACTION_CHOICES = (
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('VIEW', 'View'),
        ('EXPORT', 'Export'),
        ('IMPORT', 'Import'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField(blank=True, null=True)
    model_name = models.CharField(max_length=50, blank=True, null=True)  # Which model was affected
    object_id = models.PositiveIntegerField(blank=True, null=True)  # ID of affected object
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} - {self.timestamp}"

    class Meta:
        verbose_name_plural = "Activities"
        ordering = ['-timestamp']