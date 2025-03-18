from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Activity
from django.utils import timezone

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a UserProfile when a new User is created
    """
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def log_user_creation(sender, instance, created, **kwargs):
    """
    Log user creation or update
    """
    if created:
        Activity.objects.create(
            user=instance,
            action='CREATE',
            description=f'User {instance.username} was created',
            model_name='User',
            object_id=instance.id,
            timestamp=timezone.now()
        )
    else:
        Activity.objects.create(
            user=instance,
            action='UPDATE',
            description=f'User {instance.username} was updated',
            model_name='User',
            object_id=instance.id,
            timestamp=timezone.now()
        )