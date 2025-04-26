from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.role_selection,name='role_selection'),
    path('home/',views.home,name='home'),
    path('about/',views.about,name='about'),
    path('contact/',views.contact,name='contact'),
    path('login/',views.login_page,name='login_page'),
    path('api/login/',views.api_login,name='api_login'),
    path('api/register/',views.api_register,name='api_register'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('logout/',views.logout_user,name='logout'),
    path('role-selection/',views.role_selection,name='role_selection_alt'),
    path('events/',views.event_poster,name='event_poster'),
    path('events/create/',views.create_event,name='create_event'),
]+static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)