from django.forms import ModelForm
from django import forms
from .models import Task,TaskAttachment,TaskComment
class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = [
            'title',
            'description',
            'priority',
            'assigned_to',
            'deadline'
        ]

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class TaskStatusUpdateForm(ModelForm):
    class Meta:
        model=Task
        fields=['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'})
        }
class TaskAttachmentForm(forms.ModelForm):
    class Meta:
        model = TaskAttachment
        fields = ['file']
class TaskCommentForm(forms.ModelForm):
    class Meta:
        model = TaskComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Write comment...'
            })
        }
