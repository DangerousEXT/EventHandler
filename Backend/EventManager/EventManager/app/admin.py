from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Profile, Event, OrganizerRequest, EventRegistration

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')
    list_editable = ('role',)
    actions = ['revoke_organizer_role']

    def revoke_organizer_role(self, request, queryset):
        queryset.update(role='participant')
        self.message_user(request, "Selected users have been revoked of organizer role.")
    revoke_organizer_role.short_description = "Revoke organizer role"

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'date', 'location')
    list_filter = ('organizer', 'date')
    search_fields = ('title', 'location')

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'created_at')
    list_filter = ('event', 'created_at')
    search_fields = ('user__username', 'event__title')

@admin.register(OrganizerRequest)
class OrganizerRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'status', 'action_links')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)
    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        for req in queryset.filter(status='pending'):
            req.status = 'approved'
            req.save()
            profile = req.user.profile
            profile.role = 'organizer'
            profile.save()
        self.message_user(request, "Selected requests have been approved.")
    approve_requests.short_description = "Approve selected requests"

    def reject_requests(self, request, queryset):
        for req in queryset.filter(status='pending'):
            req.status = 'rejected'
            req.save()
        self.message_user(request, "Selected requests have been rejected.")
    reject_requests.short_description = "Reject selected requests"

    def action_links(self, obj):
        if obj.status == 'pending':
            return '<a href="%s">Approve</a> | <a href="%s">Reject</a>' % (
                reverse('admin:approve_organizer_request', args=[obj.id]),
                reverse('admin:reject_organizer_request', args=[obj.id]),
            )
        return obj.status
    action_links.allow_tags = True
    action_links.short_description = 'Actions'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:request_id>/approve/', self.admin_site.admin_view(self.approve_request), name='approve_organizer_request'),
            path('<int:request_id>/reject/', self.admin_site.admin_view(self.reject_request), name='reject_organizer_request'),
        ]
        return custom_urls + urls

    def approve_request(self, request, request_id):
        obj = self.get_object(request, request_id)
        if obj and obj.status == 'pending':
            obj.status = 'approved'
            obj.save()
            profile = obj.user.profile
            profile.role = 'organizer'
            profile.save()
            self.message_user(request, f"Organizer request for {obj.user.username} approved.")
        return HttpResponseRedirect(reverse('admin:app_organizerrequest_changelist'))

    def reject_request(self, request, request_id):
        obj = self.get_object(request, request_id)
        if obj and obj.status == 'pending':
            obj.status = 'rejected'
            obj.save()
            self.message_user(request, f"Organizer request for {obj.user.username} rejected.")
        return HttpResponseRedirect(reverse('admin:app_organizerrequest_changelist'))