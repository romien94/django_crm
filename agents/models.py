from django.db import models
from django.contrib.auth import get_user_model

from leads.models import UserProfile

User = get_user_model()


class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email
