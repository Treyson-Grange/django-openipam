from django.urls import include, path

from rest_framework import routers
from . import views
from .views import misc


router = routers.DefaultRouter()
router.register(r"hosts", views.hosts.HostViewSet)
router.register(r"dns", views.dns.DnsViewSet)
router.register(r"dns/dhcp", views.dns.DhcpDnsViewSet)
router.register(r"domains", views.dns.DomainViewSet)
router.register(r"attributes", misc.AttributeViewSet)
router.register(r"networks", views.network.NetworkViewSet)
router.register(r"networks/network-range", views.network.NetworkRangeViewSet)
router.register(r"networks/network-to-vlans", views.network.NetworkToVlanViewSet)
router.register(r"pools", views.network.AddressPoolViewSet)
router.register(r"vlans", views.network.VlanViewSet)
router.register(r"default-pools", views.network.DefaultPoolViewSet)
router.register(r"dhcp/groups", views.network.DhcpGroupViewSet)
router.register(r"dhcp/options", views.network.DhcpOptionViewSet)
router.register(r"dhcp/options-to-groups", views.network.DhcpOptionToGroupViewSet)
router.register(r"users", views.users.UserViewSet)
router.register(r"addresses", views.network.AddressViewSet)
router.register(r"addresses/types", views.network.AddressTypeViewSet)
router.register(r"logs", views.logs.LogViewSet)
router.register(r"leases", views.network.LeaseViewSet)
router.register(r"buildings", views.network.BuildingViewSet)
router.register(r"building-to-vlans", views.network.BuildingToVlanViewSet)
router.register(r"report/exposed-server-hosts", views.report.ExposedHostViewSet)
router.register(r"report/disabled-hosts", views.report.DisabledHostsViewSet)
router.register(r"report/host-dns", views.report.HostDNSViewSet)
router.register(r"report/ptrdns", views.report.PTRDNSViewSet)
router.register(r"report/expired-hosts", views.report.ExpiredHostsViewSet)
router.register(r"report/orphaned-dns", views.report.OrphanedDNSViewSet)
router.register(r"report/recent-stats", views.report.RecentStatsViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("admin/stats/", misc.DashboardAPIView.as_view()),
    path("groups/", views.users.GroupView.as_view()),
    path("login/", views.auth.login_request, name="login"),
    path("get_csrf/", views.auth.get_csrf_token, name="get_csrf"),
    path("logout/", views.auth.logout_request, name="logout"),
    path("whoami/", views.auth.whoami, name="whoami"),
]
