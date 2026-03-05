from django.db import models
from .constants  import Roles
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    ROLE_CHOICES=(
        (Roles.ADMIN,'ADMIN'),
        (Roles.MD,'MANAGING DIRECTOR'),
        (Roles.DEPARTMENT,'DEPARTMENT')
    )
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='userprofile')
    dept=models.CharField(max_length=200,null=True)
    role=models.CharField(max_length=200,choices=ROLE_CHOICES)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username}"

    