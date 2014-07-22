from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import localtime
from django import forms

from openipam.log.models import HostLog, EmailLog

import autocomplete_light

User = get_user_model()


class LogEntryAdminForm(forms.ModelForm):
    user = autocomplete_light.ModelChoiceField('UserAutocomplete')
    content_type = autocomplete_light.ModelChoiceField('ContentTypeAutocomplete')


    class Meta:
        model = LogEntry


class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('object_name', 'object_id', 'action_name', 'user', 'change_time',)
    list_filter = ('action_time',)
    search_fields = ('object_repr', 'object_id', 'user__username')
    form = LogEntryAdminForm

    def get_queryset(self, request):
        qs = super(LogEntryAdmin, self).get_queryset(request)
        return qs.select_related('content_type')

    def change_time(self, obj):
        return '<span class="nowrap">%s</span>' % localtime(obj.action_time).strftime("%d %b %Y %H:%M:%S")
    change_time.short_description = 'Timestamp'
    change_time.admin_order_field = 'action_time'
    change_time.allow_tags = True

    def action_name(self, obj):
        if obj.action_flag == 1:
            return 'Addition'
        elif obj.action_flag == 2:
            return 'Changed'
        elif obj.action_flag == 3:
            return 'Deletion'
    action_name.short_description = 'Action'

    def object_name(self, obj):
        return '%s: %s' % (obj.content_type.model.capitalize(), obj.object_repr)
    object_name.short_description = 'Model object'


class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('to', 'when', 'subject',)
    list_filter = ('when',)
    readonly_fields = ('when', 'to', 'subject', 'email_body',)
    search_fields = ('subject', 'body', 'to',)
    exclude = ('body',)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class HostLogAdmin(admin.ModelAdmin):
    list_display = ('mac', 'hostname', 'changed', 'changed_by',)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


admin.site.register(EmailLog, EmailLogAdmin)
admin.site.register(LogEntry, LogEntryAdmin)
admin.site.register(HostLog, HostLogAdmin)
