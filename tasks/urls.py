from django.urls import path
from . import views

urlpatterns=[
    path('login/',views.loginPage,name='login'),
    path('logout/',views.logoutUser,name='logout'),
    path('',views.home,name='home'),
    path('dashboard',views.admin_dashboard,name='admin_dashboard'),
    path('employee/<str:pk>/',views.employee_dashboard,name='employee'),
    path('assigntask',views.assign_task,name='assign_task'),
    path('update_status/<str:pk>/',views.update_task_status,name='update_status'),
    path('department_dashboard/<str:dept>/',views.department_dashboard,name='department'),
    path('add-comment/<int:task_id>/', views.add_comment, name='add_comment'),
    path('delete-comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('delete-task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('approve-task/<int:pk>/', views.approve_task, name="approve_task"),
    path('reject-task/<int:pk>/', views.reject_task, name="reject_task"),
    path('superadmin-dashboard/', views.superadmin_dashboard, name='superadmin_dashboard'),

]