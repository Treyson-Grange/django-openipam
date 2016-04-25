from django.conf.urls import patterns, url, include
from openipam.api.views.base import UserAuthenticated
from openipam.api.views import network
from openipam.api.views import hosts
from openipam.api.views import users
from openipam.api.views import guests
from openipam.api.views import dns
from openipam.api.views import report
from rest_framework_jwt.views import obtain_jwt_token

# router = DefaultRouter()
# router.register('hosts2', HostViewSet)


urlpatterns = patterns('openipam.api.views',

    #url(r'^', include(router.urls)),

    url(r'^web/networkselects/(?P<address_type_id>\d+)$', 'web.network_selects', name='api_network_select'),
    url(r'^web/structuredattributevalues/(?P<attribute_id>\d+)$', 'web.structured_attribute_selects', name='api_structured_attribute_select'),
    url(r'^web/', include('autocomplete_light.urls')),

    #Reports
    url(r'^reports/serverhosts/$', report.server_hosts, name='api_reports_server_hosts'),
    url(r'^reports/subnetdata/$', report.subnet_data, name='api_reports_subnet_data'),
    url(r'^reports/weatherdata/$', report.weather_data, name='api_reports_weather_data'),
    url(r'^reports/hoststats/$', report.host_stats, name='api_reports_host_stats'),
    url(r'^reports/leasestats/$', report.lease_stats, name='api_reports_lease_stats'),
    url(r'^reports/leasegraph/(?P<network>.*)/$', report.render_lease_chart, name='api_reports_lease_graph'),

    # Users
    url(r'^users/$', users.UserList.as_view(), name='api_users_list'),
    # Groups
    url(r'^groups/$', users.GroupList.as_view(), name='api_groups_list'),
    url(r'^groups/options/$', users.GroupOptionsList.as_view(), name='api_groupsoptions_list'),

    # Attributes
    url(r'^attributes/$', hosts.AttributeList.as_view(), name='api_attributes'),
    url(r'^attributes/structured/values/$', hosts.StructuredAttributeValueList.as_view(), name='api_attributes_structured_values'),

    # Hosts
    url(r'^hosts/mac/next/$', hosts.HostNextMac.as_view(), name='api_host_mac_next'),
    url(r'^hosts/mac/$', hosts.HostMac.as_view(), name='api_host_mac'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/attributes/add/$', hosts.HostAddAttribute.as_view(), name='api_host_attribute_add'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/attributes/delete/$', hosts.HostDeleteAttribute.as_view(), name='api_host_attribute_delete'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/attributes/$', hosts.HostAttributeList.as_view(), name='api_host_attribute_list'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/owners/add/$', hosts.HostOwnerAdd.as_view(), name='api_host_owners_delete'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/owners/delete/$', hosts.HostOwnerDelete.as_view(), name='api_host_owners_add'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/owners/$', hosts.HostOwnerList.as_view(), name='api_host_owners_list'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/renew/$', hosts.HostRenew.as_view(), name='api_host_renew'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/update/$', hosts.HostUpdate.as_view(), name='api_host_update'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/delete/$', hosts.HostDelete.as_view(), name='api_host_delete'),
    url(r'^hosts/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/$', hosts.HostDetail.as_view(), name='api_host_view'),
    url(r'^hosts/add/$', hosts.HostCreate.as_view(), name='api_host_add'),
    url(r'^hosts/disabled/(?P<pk>([0-9a-fA-F]{2}[:-]?){5}[0-9a-fA-F]{2})/delete/$', hosts.DisabledHostDelete.as_view(), name='api_disabled_hosts_delete'),
    url(r'^hosts/disabled/add/$', hosts.DisabledHostCreate.as_view(), name='api_disabled_hosts_add'),
    url(r'^hosts/disabled/$', hosts.DisabledHostList.as_view(), name='api_disabled_hosts_list'),
    url(r'^hosts/$', hosts.HostList.as_view(), name='api_host_list'),

    url(r'^guests/register/$', guests.GuestRegister.as_view(), name='api_guest_register'),
    url(r'^guests/tickets/add/$', guests.GuestTicketCreate.as_view(), name='api_guest_create'),
    url(r'^guests/tickets/$', guests.GuestTicketList.as_view(), name='api_guest_list'),
    url(r'^guests/tickets/(?P<ticket>\w+)/$', guests.GuestTicketDelete.as_view(), name='api_guest_delete'),

    url(r'^domain/$', dns.DomainList.as_view(), name='api_domain_list'),
    url(r'^domain/name/$', dns.DomainNameList.as_view(), name='api_domain_name_list'),
    url(r'^network/$', network.NetworkList.as_view(), name='api_network_list'),
    url(r'^address/(?P<pk>(\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3}))/$', network.AddressDetail.as_view(), name='api_address_view'),
    url(r'^address/$', network.AddressList.as_view(), name='api_address_list'),
    url(r'^dhcpgroup/$', network.DhcpGroupList.as_view(), name='api_dhcpgroup_list'),

    url(r'^login/has_auth/', UserAuthenticated.as_view(), name='api_has_auth'),
    url(r'^login/jwt_token/', obtain_jwt_token),
    url(r'^', include('rest_framework.urls', namespace='rest_framework')),
)
