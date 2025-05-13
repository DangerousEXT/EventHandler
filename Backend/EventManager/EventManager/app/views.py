from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Event, Profile, OrganizerRequest, EventRegistration, Item
from django.views.decorators.csrf import ensure_csrf_cookie
import json

@ensure_csrf_cookie
def login_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'app/index.html', {'title': 'Login'})

@login_required
def dashboard(request):
    events = Event.objects.all()
    return render(request, 'app/dashboard.html', {'events': events})

@login_required
def event_poster(request):
    if not request.user.is_authenticated or request.user.profile.role != 'organizer':
        return redirect('dashboard')
    return render(request, 'app/event_poster.html')

@login_required
def event_attendees(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'organizer':
        return redirect('dashboard')
    events = Event.objects.filter(organizer=request.user).order_by('date')
    print(f"User: {request.user.username}, Events: {events.count()}")
    for event in events:
        print(f"Event: {event.title}, Attendees: {event.registrations.count()}")
    return render(request, 'app/event_attendees.html', {'events': events})

def about(request):
    return render(request, 'app/about.html')

def contact(request):
    return render(request, 'app/contact.html')

def shop(request):
    items = Item.objects.all().order_by('-created_at')  # Newest first
    return render(request, 'app/shop.html', {'items': items})

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
                profile, created = Profile.objects.get_or_create(user=user, defaults={'role': 'participant'})
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
            Profile.objects.create(user=user, role='participant')
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
            return JsonResponse({'status': 'success', 'message': 'Organizer request submitted'})
        except Profile.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Profile not found'})
        except IntegrityError:
            return JsonResponse({'status': 'error', 'message': 'Database error'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Server error: {str(e)}'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request or user not authenticated'})

@login_required
def api_create_event(request):
    if request.user.profile.role != 'organizer':
        return JsonResponse({'status': 'error', 'message': 'Only organizers can create events.'})

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        date_str = request.POST.get('date')
        location = request.POST.get('location')
        image = request.FILES.get('image')

        try:
            date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            if timezone.is_aware(timezone.now()):
                date = timezone.make_aware(date, timezone=timezone.get_current_timezone())
            now = timezone.now()
            if date < now:
                return JsonResponse({'status': 'error', 'message': 'Event date cannot be in the past.'})
            max_date = datetime(2125, 12, 31, 23, 59)
            if timezone.is_aware(timezone.now()):
                max_date = timezone.make_aware(max_date, timezone=timezone.get_current_timezone())
            if date > max_date:
                return JsonResponse({'status': 'error', 'message': 'Event date cannot be after 2125.'})

            event = Event(
                title=title,
                description=description,
                date=date,
                location=location,
                organizer=request.user,
                image=image
            )
            event.save()

            return JsonResponse({'status': 'success', 'message': 'Event created successfully!'})
        except ValueError as e:
            return JsonResponse({'status': 'error', 'message': f'Invalid date format: {str(e)}'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Server error: {str(e)}'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

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

def api_leave_event(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            data = json.loads(request.body)
            event_id = data.get('event_id')
            if not event_id:
                return JsonResponse({'status': 'error', 'message': 'Event ID is required'})
            event = Event.objects.get(id=event_id)
            registration = EventRegistration.objects.filter(user=request.user, event=event)
            if not registration.exists():
                return JsonResponse({'status': 'error', 'message': 'You are not registered'})
            registration.delete()
            return JsonResponse({'status': 'success', 'message': 'Successfully unregistered from the event'})
        except Event.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Event not found'})
        except IntegrityError:
            return JsonResponse({'status': 'error', 'message': 'Database error'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Server error: {str(e)}'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request or user not authenticated'})