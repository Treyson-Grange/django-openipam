from django.conf.urls import url, include

from rest_framework_jwt.views import obtain_jwt_token

from openipam.api import views

# router = DefaultRouter()
# router.register('hosts2', HostViewSet)

urlpatterns = [
    # url(r'^', include(router.urls)),

    url(r'^web/networkselects/(?P<address_type_id>\d+)$', views.web.network_selects, name='api_network_select'),
    url(r'^web/structuredattributevalues/(?P<attribute_id>\d+)$', views.web.structured_attribute_selects, name='api_structured_attribute_select'),
    url(r'^web/', include('autocomplete_light.urls')),

    # Reports
    url(r'^reports/serverhosts/$', views.report.server_hosts, name='api_reports_server_hosts'),
    url(r'^reports/subnetdata/$', views.report.subnet_data, name='api_reports_subnet_data'),
    url(r'^reports/weatherdata/$', views.report.weather_data, name='api_reports_weather_data'),
    url(r'^reports/hoststats/$', views.report.host_stats, name='api_reports_host_stats'),
    url(r'^reports/leasestats/$', views.report.lease_stats, name='api_reports_lease_stats'),
    url(r'^reports/leasegraph/(?P<network>.*)/$', views.report.render_lease_chart, name='api_reports_lease_graph'),

    # Users
    url(r'^users/$', views.users.UserList.as_view(), name='api_users_list'),
    # Groups
    url(r'^groups/$', views.users.GroupList.as_view(), name='api_groups_list'),
    url(r'^groups/options/$', views.users.GroupOptionsList.as_view(), name='api_groupsoptions_list'),

    # Attributes
    url(r'^attributes/$', views.hosts.AttributeList.as_view(), name='api_attributes'),
    url(r'^attributes/structured/values/$', views.hosts.StructuredAttributeValueList.as_view(), name='api_attributes_structured_values'),

    # Hosts
    url(r'^hosts/mac/next/$', views.hosts.HostNextMac.as_view(), name='api_host_mac_next'),
    url(r'^hosts/mac/$', views.hosts.HostMac.as_view(), name='api_host_mac'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/attributes/add/$', views.hosts.HostAddAttribute.as_view(), name='api_host_attribute_add'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/attributes/delete/$', views.hosts.HostDeleteAttribute.as_view(), name='api_host_attribute_delete'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/attributes/$', views.hosts.HostAttributeList.as_view(), name='api_host_attribute_list'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/owners/add/$', views.hosts.HostOwnerAdd.as_view(), name='api_host_owners_delete'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/owners/delete/$', views.hosts.HostOwnerDelete.as_view(), name='api_host_owners_add'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/owners/$', views.hosts.HostOwnerList.as_view(), name='api_host_owners_list'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/renew/$', views.hosts.HostRenew.as_view(), name='api_host_renew'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/update/$', views.hosts.HostUpdate.as_view(), name='api_host_update'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/delete/$', views.hosts.HostDelete.as_view(), name='api_host_delete'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/$', views.hosts.HostDetail.as_view(), name='api_host_view'),
    url(r'^hosts/add/$', views.hosts.HostCreate.as_view(), name='api_host_add'),
    url(r'^hosts/disabled/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/delete/$', views.hosts.DisabledHostDelete.as_view(), name='api_disabled_hosts_delete'),
    url(r'^hosts/disabled/add/$', views.hosts.DisabledHostCreate.as_view(), name='api_disabled_hosts_add'),
    url(r'^hosts/disabled/$', views.hosts.DisabledHostList.as_view(), name='api_disabled_hosts_list'),
    url(r'^hosts/$', views.hosts.HostList.as_view(), name='api_host_list'),

    url(r'^guests/register/$', views.guests.GuestRegister.as_view(), name='api_guest_register'),
    url(r'^guests/tickets/add/$', views.guests.GuestTicketCreate.as_view(), name='api_guest_create'),
    url(r'^guests/tickets/$', views.guests.GuestTicketList.as_view(), name='api_guest_list'),
    url(r'^guests/tickets/(?P<ticket>\w+)/$', views.guests.GuestTicketDelete.as_view(), name='api_guest_delete'),

    url(r'^domain/$', views.dns.DomainList.as_view(), name='api_domain_list'),
    url(r'^domain/name/$', views.dns.DomainNameList.as_view(), name='api_domain_name_list'),
    url(r'^network/$', views.network.NetworkList.as_view(), name='api_network_list'),
    url(r'^address/(?P<pk>(\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3}))/$', views.network.AddressDetail.as_view(), name='api_address_view'),
    url(r'^address/$', views.network.AddressList.as_view(), name='api_address_list'),
    url(r'^dhcpgroup/$', views.network.DhcpGroupList.as_view(), name='api_dhcpgroup_list'),

    url(r'^login/has_auth/', views.base.UserAuthenticated.as_view(), name='api_has_auth'),
    url(r'^login/jwt_token/', views.base.obtain_jwt_token),
    url(r'^', include('rest_framework.urls', namespace='rest_framework')),
]
