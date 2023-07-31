from django.urls import include, path

from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r"hosts", views.hosts.HostViewSet)
router.register(r"dns", views.dns.DnsViewSet)
router.register(r"domains", views.dns.DomainViewSet)

# TODO: figure out how to get CSRF protection working with the new API
urlpatterns = [
    path("", include(router.urls)),
    path('domains/<name>/',
         csrf_exempt(views.dns.DomainViewSet.as_view({'get': 'retrieve',
                                                      'patch': 'partial_update',
                                                      'delete': 'destroy',
                                                      'post': 'add_dns_record'})), name='api_domain_dns_list'),
    path(
        "dns-types/",
        csrf_exempt(views.dns.DnsTypeList.as_view()),
        name="api_dns_type_list",
    ),
    path(
        "dns-views/",
        csrf_exempt(views.dns.DnsViewsList.as_view()),
        name="api_dns_view_list",
    ),
    path(
        "dhcp-dns/",
        csrf_exempt(views.dns.DhcpDnsRecordsList.as_view()),
        name="api_dhcp_dns_list",
    ),
    path("admin/logs/", csrf_exempt(views.admin.LogEntryList.as_view())),
    path("admin/logs/hosts/", csrf_exempt(views.admin.HostLogsList.as_view())),
    path("admin/logs/emails/", csrf_exempt(views.admin.EmailLogsList.as_view())),
    path("admin/logs/dns/", csrf_exempt(views.admin.DnsLogsList.as_view())),
    path("admin/logs/addresses/", csrf_exempt(views.admin.AddressLogsList.as_view())),
    path("admin/logs/users/", csrf_exempt(views.admin.UserLogsList.as_view())),
    # Host disable/enable
    path(
        "hosts/<str:mac>/disabled/",
        csrf_exempt(views.hosts.DisableView.as_view()),
        name="host-disable",
    ),
    path(
        "hosts/<str:mac>/users/",
        csrf_exempt(views.hosts.UserOwnerView.as_view()),
        name="host-users",
    ),
    path(
        "hosts/<str:mac>/groups/",
        csrf_exempt(views.hosts.GroupOwnerView.as_view()),
        name="host-groups",
    ),
    path(
        "hosts/<str:mac>/groups/<str:groupname>/",
        csrf_exempt(views.hosts.GroupOwnerView.as_view()),
        name="host-groups-specific",
    ),
    path(
        "hosts/<str:mac>/users/<str:username>/",
        csrf_exempt(views.hosts.UserOwnerView.as_view()),
        name="host-users-specific",
    ),
    path(
        "hosts/<str:mac>/attributes/",
        csrf_exempt(views.hosts.HostAttributesView.as_view()),
        name="host-attributes",
    ),
    path(
        "hosts/<str:mac>/addresses/",
        csrf_exempt(views.hosts.AddressView.as_view()),
        name="host-addresses",
    ),
    path(
        "hosts/<str:mac>/addresses/<str:address>/",
        csrf_exempt(views.hosts.AddressView.as_view()),
        name="host-addresses-specific",
    ),
    path(
        "hosts/<str:mac>/leases/",
        csrf_exempt(views.hosts.LeasesView.as_view()),
        name="host-leases",
    ),
]
