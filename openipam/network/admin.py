from django.contrib import admin
from django import forms
from django.shortcuts import redirect, render
from django.conf.urls import url
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from openipam.network.models import Network, NetworkRange, Address, Pool, DhcpGroup, \
    Vlan, AddressType, DefaultPool, DhcpOptionToDhcpGroup, Lease, DhcpOption, SharedNetwork, \
    NetworkToVlan
from openipam.network.forms import NetworkTagForm, AddressTypeAdminForm, DhcpOptionToDhcpGroupAdminForm, \
    AddressAdminForm, LeaseAdminForm
from openipam.core.admin import ChangedAdmin

import autocomplete_light


class NetworkAdmin(ChangedAdmin):
    form = autocomplete_light.modelform_factory(Network)
    list_display = ('nice_network', 'name', 'description', 'gateway')
    list_filter = ('tags', 'shared_network__name')
    search_fields = ('network', 'shared_network__name')
    actions = ['tag_network', 'release_abandoned_leases']

    def get_actions(self, request):
        #Disable delete
        actions = super(NetworkAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def nice_network(self, obj):
        url = str(obj.network).replace('/', '_2F')
        return '<a href="./%s/">%s</a>' % (url, obj.network)
    nice_network.short_description = 'Network'
    nice_network.allow_tags = True

    def get_urls(self):
        urls = super(NetworkAdmin, self).get_urls()
        net_urls = [
            url(r'^tag/$', self.tag_network_view),
        ]
        return net_urls + urls

    def tag_network_view(self, request):
        form = NetworkTagForm(request.POST or None)

        if form.is_valid():
            ids = request.REQUEST.get('ids').strip().split(',')
            networks = Network.objects.filter(pk__in=ids)

            for network in networks:
                network.tags.add(*form.cleaned_data['tags'])

            return redirect('../')

        return render(request, 'admin/actions/tag_network.html', {'form': form})

    def tag_network(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        ct = ContentType.objects.get_for_model(queryset.model)
        return redirect("tag/?ct=%s&ids=%s" % (ct.pk, ",".join(selected)))

    def release_abandoned_leases(self, request, queryset):
        for network in queryset:
            Lease.objects.filter(
                address__address__net_contained_or_equal=network.network,
                abandoned=True).update(abandoned=False, host='000000000000')

    def save_model(self, request, obj, form, change):
        super(NetworkAdmin, self).save_model(request, obj, form, change)

        if not change:
            addresses = []
            for address in obj.network:
                reserved = False
                if address in (obj.gateway, obj.network[0], obj.network[-1]):
                    reserved = True
                pool = DefaultPool.objects.get_pool_default(address) if not reserved else None
                addresses.append(
                    #TODO: Need to set pool eventually.
                    Address(
                        address=address,
                        network=obj,
                        reserved=reserved,
                        pool=pool,
                        changed_by=request.user,
                    )
                )
            Address.objects.bulk_create(addresses)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(NetworkAdmin, self).get_search_results(request, queryset, search_term)
        queryset = queryset | Network.searcher.search(search_term)

        return queryset, use_distinct


class AddressTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'show_pool', 'show_ranges', 'is_default')
    form = AddressTypeAdminForm
    list_select_related = True

    def get_queryset(self, request):
        qs = super(AddressTypeAdmin, self).get_queryset(request)
        return qs.prefetch_related('ranges', 'pool').all()

    def show_pool(self, obj):
        return obj.pool if obj.pool else ''
    show_pool.short_description = 'Network Pool'

    def show_ranges(self, obj):
        ranges = [str(range) for range in obj.ranges.all()]
        return '%s' % '<br />'.join(ranges) if ranges else ''
    show_ranges.short_description = 'Network Ranges'
    show_ranges.allow_tags = True


class DhcpGroupAdmin(ChangedAdmin):
    form = autocomplete_light.modelform_factory(DhcpGroup)


class DhcpOptionToDhcpGroupAdmin(ChangedAdmin):
    list_display = ('combined_value', 'changed', 'changed_by',)
    form = DhcpOptionToDhcpGroupAdminForm
    fields = ('group', 'option', 'readable_value', 'changed', 'changed_by',)
    readonly_fields = ('changed_by', 'changed',)
    list_select_related = True

    def combined_value(self, obj):
        return '%s:%s=%r' % (obj.group.name, obj.option.name, str(obj.value))
    combined_value.short_description = 'Group:Option=Value'

    def get_queryset(self, request):
        qs = super(DhcpOptionToDhcpGroupAdmin, self).get_queryset(request)
        return qs.prefetch_related('group', 'option').all()

    # def get_form(self, request, obj=None, **kwargs):
    #     super(DhcpOptionToDhcpGroupAdmin, self).get_form(request, obj, **kwargs)


class DefaultPoolAdmin(admin.ModelAdmin):
    list_select_related = True

    def get_queryset(self, request):
        qs = super(DefaultPoolAdmin, self).get_queryset(request)
        return qs.select_related('pool').all()


class PoolAdmin(admin.ModelAdmin):
    pass


class SharedNetworkAdmin(ChangedAdmin):
    list_display = ('name', 'description', 'changed_by', 'changed',)


class VlanAdmin(ChangedAdmin):
    pass


class NetworkToVlanAdmin(ChangedAdmin):
    list_display = ('network', 'vlan', 'changed_by', 'changed',)


class IsExpiredFilter(admin.SimpleListFilter):
    title = 'is expired'
    parameter_name = 'is_expired'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Yes'),
            ('0', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(ends__lte=timezone.now())
        if self.value() == '0':
            return queryset.filter(ends__gt=timezone.now())


class LeaseAdmin(admin.ModelAdmin):
    form = LeaseAdminForm
    #form = autocomplete_light.modelform_factory(Lease)
    list_display = ('address', 'mac', 'starts', 'ends', 'server', 'abandoned',)
    search_fields = ('address__address', 'host__mac', 'host__hostname',)
    list_filter = ('abandoned', 'starts', 'ends', 'server', IsExpiredFilter)

    def save_model(self, request, obj, form, change):
        obj.host_id = form.cleaned_data['host']
        obj.save()

    def mac(self, obj):
        return obj.host_id
    mac.short_description = 'Host'


class HasHostFilter(admin.SimpleListFilter):
    title = 'has host'
    parameter_name = 'has_host'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Yes'),
            ('0', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(host__isnull=False)
        if self.value() == '0':
            return queryset.filter(host__isnull=True)


class AddressAdmin(ChangedAdmin):
    form = AddressAdminForm
    search_fields = ('address', 'host__mac', 'host__hostname',)
    list_filter = ('network', 'reserved', 'pool', HasHostFilter)
    list_display = ('address', 'network', 'host', 'pool', 'reserved', 'changed_by', 'changed')
    list_select_related = True

    def get_queryset(self, request):
        qs = super(AddressAdmin, self).get_queryset(request)
        return qs.select_related('host', 'network', 'changed_by').all()


admin.site.register(DefaultPool, DefaultPoolAdmin)
admin.site.register(NetworkToVlan, NetworkToVlanAdmin)
admin.site.register(SharedNetwork, SharedNetworkAdmin)
admin.site.register(DhcpOption)
admin.site.register(Vlan, ChangedAdmin)
admin.site.register(NetworkRange)
admin.site.register(Network, NetworkAdmin)
admin.site.register(Lease, LeaseAdmin)
admin.site.register(AddressType, AddressTypeAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Pool, PoolAdmin)
admin.site.register(DhcpGroup, DhcpGroupAdmin)
admin.site.register(DhcpOptionToDhcpGroup, DhcpOptionToDhcpGroupAdmin)
