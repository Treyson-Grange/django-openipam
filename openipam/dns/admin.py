from django.contrib import admin
from models import DnsRecord, DnsType, Domain
from guardian.admin import GuardedModelAdmin
import autocomplete_light


class DomainAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Domain)
    change_form_template = 'admin/openipam/change_form.html'


class DnsRecordAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(DnsRecord)
    change_form_template = 'admin/openipam/change_form.html'


class DnsTypeAdmin(GuardedModelAdmin):
    list_display = ('name', 'description', 'min_permission')

    def min_permission(self, obj):
        return '%s' % obj.min_permissions.name


admin.site.register(DnsType, DnsTypeAdmin)
admin.site.register(DnsRecord, DnsRecordAdmin)
admin.site.register(Domain, DomainAdmin)
