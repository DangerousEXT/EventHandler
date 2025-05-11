from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Event, Profile
import json

def login_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'app/index.html', {'title': 'Login'})

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login_page')
    events = Event.objects.all()
    return render(request, 'app/dashboard.html', {'title': 'Dashboard', 'events': events})

def event_poster(request):
    events = Event.objects.all()
    return render(request, 'app/event_poster.html', {'title': 'Events', 'events': events})

def about(request):
    return render(request, 'app/about.html', {'title': 'About'})

def contact(request):
    return render(request, 'app/contact.html', {'title': 'Contact'})

def logout_view(request):
    logout(request)
    return redirect('login_page')

def api_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            profile, created = Profile.objects.get_or_create(user=user)
            profile.role = role
            profile.save()
            return JsonResponse({'status': 'success', 'redirect': '/dashboard/'})
        return JsonResponse({'status': 'error', 'message': 'Invalid credentials'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def api_register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        role = data.get('role')
        if password != confirm_password:
            return JsonResponse({'status': 'error', 'message': 'Passwords do not match'})
        if User.objects.filter(username=username).exists():
            return JsonResponse({'status': 'error', 'message': 'Username already exists'})
        user = User.objects.create_user(username=username, password=password)
        profile = Profile.objects.create(user=user, role=role)
        login(request, user)
        return JsonResponse({'status': 'success', 'redirect': '/dashboard/'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def api_change_role(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        role = data.get('role')
        if role not in ['participant', 'organizer']:
            return JsonResponse({'status': 'error', 'message': 'Invalid role'})
        profile = Profile.objects.get(user=request.user)
        profile.role = role
        profile.save()
        return JsonResponse({'status': 'success', 'redirect': '/dashboard/'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request or user not authenticated'})