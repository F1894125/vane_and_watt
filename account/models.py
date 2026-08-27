from django.db import models
from django.conf import settings
from django.urls import reverse


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    date_of_birth = models.DateField()
    photo = models.ImageField(
        upload_to='users/%Y/%m/%d/',
        default='users/default.jpg'
    )

    def __str__(self):
        return f'Profile for user {self.user.username}'

    def get_absolute_url(self):
        """Returns the canonical API URL for this profile."""
        return reverse(
            "account:profile_form",
            kwargs={"username": self.user.username}
        )
    