from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login_page'),
    path('login/', views.login_page, name='login_page'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('event_poster/', views.event_poster, name='event_poster'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('logout/', views.logout_view, name='logout'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/register/', views.api_register, name='api_register'),
]