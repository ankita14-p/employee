import django_filters
from django import forms
from .models import Task


class OrderFilter(django_filters.FilterSet):

    status = django_filters.ChoiceFilter(
        choices=Task.STATUS,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )

    approval_status = django_filters.ChoiceFilter(
        choices=Task.APPROVAL,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )

    class Meta:
        model = Task
        fields = ['status', 'approval_status']
