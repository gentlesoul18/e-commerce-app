from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile
from random import randint


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):

    if created:
        Profile.objects.create(user=instance)

    print("NEW PROFILE WAS CREATED!")

post_save.connect(create_profile, sender=User)
