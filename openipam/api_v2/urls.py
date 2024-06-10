from django.urls import include, path

from rest_framework import routers
from . import views
from .views import misc


router = routers.DefaultRouter()
router.register(r"hosts", views.hosts.HostViewSet)
router.register(r"dns", views.dns.DnsViewSet)
router.register(r"dhcp", views.dns.DhcpDnsViewSet)
router.register(r"domains", views.dns.DomainViewSet)
router.register(r"attributes", misc.AttributeViewSet)
router.register(r"networks", views.network.NetworkViewSet)
router.register(r"network-ranges", views.network.NetworkRangeViewSet)
router.register(r"shared-networks", views.network.SharedNetworkViewSet)
router.register(r"pools", views.network.AddressPoolViewSet)
router.register(r"dhcp-groups", views.network.DhcpGroupViewSet)
router.register(r"dhcp-option", views.network.DhcpOptionViewSet)
router.register(r"dhcp-option-to-groups", views.network.DhcpOptionToGroupViewSet)
router.register(r"users", views.users.UserViewSet)
router.register(r"addresses", views.network.AddressViewSet)
router.register(r"address-types", views.network.AddressTypeViewSet)
router.register(r"logs", views.logs.LogViewSet)
router.register(r"building", views.network.BuildingViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("admin/stats/", misc.DashboardAPIView.as_view()),
    path("groups/", views.users.GroupView.as_view()),
]
