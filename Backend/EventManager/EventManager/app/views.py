from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Event
import json
from datetime import timedelta

def role_selection(request):
    if 'role' in request.session:
        return redirect('event_poster')
    if request.method=='POST':
        role=request.POST.get('role')
        request.session['role']=role
        return redirect('event_poster')
    return render(request,'app/role_selection.html')

def event_poster(request):
    if 'role' not in request.session:
        return redirect('role_selection')
    query=request.GET.get('search','')
    events=Event.objects.all()
    if query:
        events=events.filter(title__icontains=query)
    return render(request,'app/event_poster.html',{'events':events,'query':query})

@csrf_exempt
def create_event(request):
    if request.session.get('role')!='organizer' or not request.user.is_authenticated:
        return redirect('role_selection')
    if request.method=='POST':
        title=request.POST.get('title')
        description=request.POST.get('description')
        date_time=request.POST.get('date_time')
        category=request.POST.get('category')
        image=request.FILES.get('image')
        event=Event.objects.create(
            title=title,description=description,date_time=date_time,
            category=category,image=image,organizer=request.user
        )
        return redirect('dashboard')
    return render(request,'app/create_event.html')

def login_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('dashboard')
        else:
            return render(request,'app/index.html',{'error':'Invalid credentials'})
    return render(request,'app/index.html')

@csrf_exempt
def api_login(request):
    if request.method=='POST':
        data=json.loads(request.body)
        username=data.get('username')
        password=data.get('password')
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return JsonResponse({'status':'success','redirect':'/dashboard/'})
        else:
            return JsonResponse({'status':'error','message':'Invalid credentials'})
    return JsonResponse({'status':'error','message':'Invalid request'},status=400)

@csrf_exempt
def api_register(request):
    if request.method=='POST':
        data=json.loads(request.body)
        username=data.get('username')
        password=data.get('password')
        confirm_password=data.get('confirm_password')
        if password!=confirm_password:
            return JsonResponse({'status':'error','message':'Passwords do not match'})
        if User.objects.filter(username=username).exists():
            return JsonResponse({'status':'error','message':'Username already exists'})
        user=User.objects.create_user(username=username,password=password)
        login(request,user)
        return JsonResponse({'status':'success','redirect':'/dashboard/'})
    return JsonResponse({'status':'error','message':'Invalid request'},status=400)

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('role_selection')
    query=request.GET.get('search','')
    if query:
        events=Event.objects.filter(title__icontains=query)|Event.objects.filter(description__icontains=query)
    else:
        events=Event.objects.all()
    context={
        'user_name':request.user.username,'events':events,
        'query':query,'role':request.session.get('role','participant')
    }
    return render(request,'app/dashboard.html',context)

def logout_user(request):
    logout(request)
    request.session.flush()
    return redirect('role_selection')

def home(request):
    return render(request,'app/index.html',{'title':'Home Page','message':'Welcome to the Event Manager'})

def about(request):
    return render(request,'app/about.html',{'title':'About','message':'Learn More About Us'})

def contact(request):
    return render(request,'app/contact.html',{'title':'Contact','message':'Get in Touch'})
