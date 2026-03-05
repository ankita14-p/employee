from django.shortcuts import render,redirect
from .forms import *
from .models import *
from user.models import UserProfile
from django.contrib.auth.models import User
from user.constants import Roles
from django.contrib import messages
from .filters import OrderFilter
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user,allowed_users
from django.http import HttpResponse

@unauthenticated_user
def loginPage(request):
    if request.method == "POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')

    else:
        messages.info(request, "Username or password didn't match")
    return render(request,'tasks/login.html')
@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    return redirect('login')
# Create your views here.
@login_required(login_url='login')
def home(request):
    user = request.user

    # ---------------- GLOBAL STATS ----------------
    total_users = User.objects.count() - 2
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(status="COMPLETED").count()

    success_rate = (
        round((completed_tasks / total_tasks) * 100)
        if total_tasks > 0 else 0
    )

    # ---------------- ALL DEPARTMENTS ----------------
    profiles = UserProfile.objects.all()

    # Get unique departments (excluding NULL/empty)
    departments = profiles.exclude(dept__isnull=True).exclude(dept='').values_list('dept', flat=True).distinct()

    department_data = []

    for dept_name in departments:
      
        # Get all tasks assigned to users in this department
        dept_tasks = Task.objects.filter(assigned_to__dept=dept_name)

        total_dept_tasks = dept_tasks.count()
        completed = dept_tasks.filter(status="COMPLETED").count()
        pending = dept_tasks.filter(status="PENDING").count()

        completion_rate = (
            round((completed / total_dept_tasks) * 100)
            if total_dept_tasks > 0 else 0
        )

        department_data.append({
            'name': dept_name,
            'total_tasks': total_dept_tasks,
            'completedd': completed,
            'pendingg': pending,
            'completion_rate': completion_rate
        })
   

    context = {
        'role': user.userprofile.role,
        'department':user.userprofile.dept,
        'total_users': total_users,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'success_rate': success_rate,
        'departments': department_data,
        'pk':user.userprofile.id
        
    }
  


    return render(request, 'tasks/main_dashboard.html', context)
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin','Super Admin'])
def admin_dashboard(request):
    departments = (
        UserProfile.objects
        .filter(role=Roles.DEPARTMENT)
        .exclude(dept__isnull=True)
        .exclude(dept__exact='')
        .values_list('dept', flat=True)
        .distinct()
    )
    tasks=Task.objects.all().order_by('-updated_at')
    myFilter=OrderFilter(request.GET,queryset=tasks)
    tasks=myFilter.qs
    task_total=tasks.count()
    pending=tasks.filter(status="PENDING").count()
    in_progress=tasks.filter(status="IN PROGRESS").count()
    completed=tasks.filter(status="COMPLETED").count()
    context={
        'departments':departments,
        'tasks':tasks,
        'total_task':task_total,
        'pending':pending,
        'in_progress':in_progress,
        'completed':completed,
        'myFilter':myFilter
    }
    return render(request,'tasks/admin_dashboard.html',context)
@login_required(login_url='login')
def employee_dashboard(request,pk):
    user = UserProfile.objects.get(id=pk)

    # show only approved tasks
    tasks = user.task_set.filter(approval_status='APPROVED')
    myFilter=OrderFilter(request.GET,queryset=tasks)
    tasks=myFilter.qs
    task_total = tasks.count()
    pending = tasks.filter(status="PENDING").count()
    in_progress = tasks.filter(status="IN PROGRESS").count()
    completed = tasks.filter(status="COMPLETED").count()

    context = {
        'user': user,
        'tasks': tasks,
        'total_task': task_total,
        'pending': pending,
        'in_progress': in_progress,
        'completed': completed,
        'myFilter':myFilter
    }
    return render(request,'tasks/employee_dashboard.html',context)

@login_required(login_url='login')
def assign_task(request):

    if request.method == 'POST':
        form = TaskForm(request.POST)

        if form.is_valid():

            task = form.save(commit=False)

            # always set creator
            task.created_by = request.user
            task.status = Status.PENDING   # set default work status


            # approval logic
            if request.user.userprofile.role == 'Super Admin':
                task.approval_status = 'APPROVED'
                task.approved_by = request.user
            else:
                task.approval_status = 'PENDING'

            task.save()
            form.save_m2m()

            # handle files
            for f in request.FILES.getlist('files'):
                TaskAttachment.objects.create(task=task, file=f)

            messages.success(request, "Task Created Successfully")

            # redirect based on role
            if request.user.userprofile.role == 'MANAGER':
                return redirect('superadmin_dashboard')
            else:
                return redirect('admin_dashboard')

        else:
            print(form.errors)   # debug in console

    else:
        form = TaskForm()

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'mode': "create"
    })



@login_required(login_url='login')
@allowed_users(allowed_roles=['Super Admin'])
def approve_task(request, pk):
    task = Task.objects.get(id=pk)
    task.approval_status = 'APPROVED'
    task.approved_by = request.user
    task.save()
    return redirect('superadmin_dashboard')


@login_required(login_url='login')
@allowed_users(allowed_roles=['Super Admin'])
def reject_task(request, pk):
    task = Task.objects.get(id=pk)
    task.approval_status = 'REJECTED'
    task.approved_by = request.user
    task.save()
    return redirect('superadmin_dashboard')

@login_required(login_url='login')
def department_dashboard(request,dept):
    tasks=Task.objects.filter(assigned_to__dept__iexact=dept)
    myFilter=OrderFilter(request.GET,queryset=tasks)
    tasks=myFilter.qs
    total_tasks=tasks.count()
    pending=tasks.filter(status="PENDING").count()
    completed=tasks.filter(status='COMPLETED').count()
    in_progress=tasks.filter(status="IN PROGRESS").count()

    context={
        'dept':dept,
        'tasks':tasks,
        'total_task':total_tasks,
        'pending':pending,
        'completed':completed,
        'in_progress':in_progress,
        'myFilter':myFilter,
    }
    return render(request,'tasks/department_dashboard.html',context)
@login_required
def update_task_status(request, pk):

    task = Task.objects.get(id=pk)

   
    if task.approval_status != 'APPROVED':
        messages.error(request, "Task is not approved yet!")
        return HttpResponse("Caannot update status of unapproved task.", status=403)

    form = TaskStatusUpdateForm(instance=task)

    if request.method == "POST":
        form = TaskStatusUpdateForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Status Updated Successfully")
            if request.user.userprofile.role == 'ADMIN':
                return redirect('admin_dashboard')
            elif request.user.userprofile.role == 'MANAGER':
                return redirect('superadmin_dashboard')
            return redirect('employee', request.user.userprofile.id)

    return render(request,'tasks/task_form.html', {
        'form':form,
        'mode':"update"
    })

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin','Super Admin'])
def add_comment(request, task_id):
    task = Task.objects.get(id=task_id)

    if request.method == "POST":
        form = TaskCommentForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.task = task
            obj.created_by = request.user
            obj.save()

    return redirect('admin_dashboard')
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin', 'Super Admin'])
def delete_comment(request, comment_id):
    comment = TaskComment.objects.get(id=comment_id)
    comment.delete()
    return redirect('admin_dashboard')
@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin','Super Admin'])
def delete_task(request, task_id):
    task = Task.objects.get(id=task_id)

    if request.method == "POST":
        task.delete()

    return redirect('admin_dashboard')
@login_required(login_url='login')
@allowed_users(allowed_roles=['Super Admin'])
def superadmin_dashboard(request):
    departments = (
        UserProfile.objects
        .filter(role=Roles.DEPARTMENT)
        .exclude(dept__isnull=True)
        .exclude(dept__exact='')
        .values_list('dept', flat=True)
        .distinct()
    )

    tasks = Task.objects.all().order_by('-updated_at')
    myFilter=OrderFilter(request.GET,queryset=tasks)
    tasks=myFilter.qs
    context = {
        'tasks': tasks,
        'total_task': tasks.count(),
        'pending': tasks.filter(status="PENDING").count(),
        'in_progress': tasks.filter(status="IN PROGRESS").count(),
        'completed': tasks.filter(status="COMPLETED").count(),
        'departments': departments,
        'myFilter':myFilter,


    }

    return render(request, 'tasks/superadmin_dashboard.html', context)