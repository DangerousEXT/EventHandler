from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta
import json
from .models import Event, Profile, OrganizerRequest, EventRegistration
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def login_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'app/index.html', {'title': 'Login'})

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login_page')
    events = Event.objects.all()
    return render(request, 'app/dashboard.html', {'events': events})

def event_poster(request):
    if not request.user.is_authenticated or request.user.profile.role != 'organizer':
        return redirect('dashboard')
    return render(request, 'app/event_poster.html')

def event_attendees(request):
    if not request.user.is_authenticated or request.user.profile.role != 'organizer':
        return redirect('dashboard')
    events = Event.objects.filter(organizer=request.user)
    selected_event = None
    attendees = []
    if 'event_id' in request.GET:
        try:
            selected_event = Event.objects.get(id=request.GET['event_id'], organizer=request.user)
            attendees = EventRegistration.objects.filter(event=selected_event)
        except Event.DoesNotExist:
            pass
    return render(request, 'app/event_attendees.html', {
        'events': events,
        'selected_event': selected_event,
        'attendees': attendees
    })

def about(request):
    return render(request, 'app/about.html')

def contact(request):
    return render(request, 'app/contact.html')

def logout_view(request):
    logout(request)
    return redirect('login_page')

def api_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            if not all([username, password]):
                return JsonResponse({'status': 'error', 'message': 'All fields are required'})
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                profile, created = Profile.objects.get_or_create(user=user, defaults={'role': 'participant', 'role_status': 'approved'})
                return JsonResponse({'status': 'success', 'redirect': '/dashboard/'})
            return JsonResponse({'status': 'error', 'message': 'Invalid credentials'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})
        except IntegrityError:
            return JsonResponse({'status': 'error', 'message': 'Database error'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Server error: {str(e)}'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def api_register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            confirm_password = data.get('confirm_password')
            if not all([username, password, confirm_password]):
                return JsonResponse({'status': 'error', 'message': 'All fields are required'})
            if password != confirm_password:
                return JsonResponse({'status': 'error', 'message': 'Passwords do not match'})
            if User.objects.filter(username=username).exists():
                return JsonResponse({'status': 'error', 'message': 'Username already exists'})
            user = User.objects.create_user(username=username, password=password)
            Profile.objects.create(user=user, role='participant', role_status='approved')
            login(request, user)
            return JsonResponse({'status': 'success', 'redirect': '/dashboard/'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})
        except IntegrityError:
            return JsonResponse({'status': 'error', 'message': 'Database error'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Server error: {str(e)}'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def api_request_organizer(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            today = timezone.now().date()
            start_of_day = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
            end_of_day = start_of_day + timedelta(days=1)
            request_count = OrganizerRequest.objects.filter(
                user=request.user,
                created_at__range=(start_of_day, end_of_day)
            ).count()
            if request_count >= 2:
                return JsonResponse({'status': 'error', 'message': 'You can only submit 2 requests per day'})
            
            OrganizerRequest.objects.create(user=request.user, status='pending')
            profile = Profile.objects.get(user=request.user)
            profile.role_status = 'pending'
            profile.save()
            return JsonResponse({'status': 'success', 'message': 'Organizer request submitted'})
        except Profile.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Profile not found'})
        except IntegrityError:
            return JsonResponse({'status': 'error', 'message': 'Database error'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Server error: {str(e)}'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request or user not authenticated'})

def api_create_event(request):
    if request.method == 'POST' and request.user.is_authenticated and request.user.profile.role == 'organizer':
        try:
            title = request.POST.get('title')
            description = request.POST.get('description')
            date = request.POST.get('date')
            location = request.POST.get('location')
            if not all([title, description, date, location]):
                return JsonResponse({'status': 'error', 'message': 'All fields are required'})
            event = Event.objects.create(
                title=title,
                description=description,
                date=date,
                location=location,
                organizer=request.user
            )
            if 'image' in request.FILES:
                event.image = request.FILES['image']
                event.save()
            return JsonResponse({'status': 'success', 'message': 'Event created successfully'})
        except IntegrityError:
            return JsonResponse({'status': 'error', 'message': 'Database error'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Server error: {str(e)}'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request or unauthorized'})

def api_join_event(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            data = json.loads(request.body)
            event_id = data.get('event_id')
            if not event_id:
                return JsonResponse({'status': 'error', 'message': 'Event ID is required'})
            event = Event.objects.get(id=event_id)
            if EventRegistration.objects.filter(user=request.user, event=event).exists():
                return JsonResponse({'status': 'error', 'message': 'You are already registered'})
            EventRegistration.objects.create(user=request.user, event=event)
            return JsonResponse({'status': 'success', 'message': 'Successfully registered for the event'})
        except Event.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Event not found'})
        except IntegrityError:
            return JsonResponse({'status': 'error', 'message': 'Database error'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Server error: {str(e)}'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request or user not authenticated'})