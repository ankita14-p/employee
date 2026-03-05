from django.db import models
from user.models import UserProfile
from .constants import  *
from django.core.exceptions import ValidationError
import os
from django.contrib.auth.models import User

# Create your models here.
class Task(models.Model):

    STATUS = (
        (Status.PENDING,'PENDING'),
        (Status.IN_PROGRESS,'IN PROGRESS'),
        (Status.COMPLETED,'COMPLETED')
    )

    PRIORITY = (
        (Priority.HIGH,'HIGH'),
        (Priority.MEDIUM,'MEDIUM'),
        (Priority.LOW,'LOW')
    )

    APPROVAL = (
        ('PENDING', 'PENDING'),
        ('APPROVED', 'APPROVED'),
        ('REJECTED', 'REJECTED'),
    )

    title = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=500, null=True)
    status = models.CharField(max_length=200, choices=STATUS, default='PENDING')
    priority = models.CharField(max_length=200, choices=PRIORITY)

    assigned_to = models.ManyToManyField(UserProfile, blank=True)
    deadline = models.DateField(null=True)

    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    approval_status = models.CharField(max_length=20, choices=APPROVAL, default='PENDING')
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="approved_tasks")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx']
    if ext.lower() not in valid_extensions:
        raise ValidationError('Unsupported file type.')


class TaskAttachment(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="attachments"
    )
    file = models.FileField(
        upload_to="task_docs/",
        validators=[validate_file_extension]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
    
class TaskComment(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    comment = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task.title} - {self.created_by.username}"

