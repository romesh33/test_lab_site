from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User)

    # The additional attributes we wish to include.
    picture = models.ImageField(upload_to='test_lab_site/static/profile_images', blank=True)

    # Override the __unicode__() method to return out something meaningful!
    def __str__(self):
        return self.user.username