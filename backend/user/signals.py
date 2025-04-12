from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile, UserPreference


@receiver(post_save, sender=User)
def create_user_related_models(sender, instance, created, **kwargs):
    if created:
        # Create Profile
        Profile.objects.create(user=instance)

        # Create NotificationSetting with default radius (optional)
        UserPreference.objects.create(
            user=instance,
            notify_radius_km=500
        )
