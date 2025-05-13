from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login_page'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('event_poster/', views.event_poster, name='event_poster'),
    path('event_attendees/', views.event_attendees, name='event_attendees'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('shop/', views.shop, name='shop'),
    path('logout/', views.logout_view, name='logout'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/register/', views.api_register, name='api_register'),
    path('api/request_organizer/', views.api_request_organizer, name='api_request_organizer'),
    path('api/create_event/', views.api_create_event, name='api_create_event'),
    path('api/join_event/', views.api_join_event, name='api_join_event'),
    path('api/leave_event/', views.api_leave_event, name='api_leave_event'),
]