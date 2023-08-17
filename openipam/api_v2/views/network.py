from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions as base_permissions, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from django.db.models import Prefetch, F

from openipam.hosts.models import Host
from ..serializers.network import (
    DhcpGroupSerializer,
    NetworkSerializer,
    AddressSerializer,
    PoolSerializer,
)
from ..filters.network import NetworkFilter, AddressFilterSet
from .base import APIPagination
from openipam.network.models import Address, DhcpGroup, Network, Pool
from netfields import NetManager  # noqa


class NetworkViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint that allows networks to be viewed"""

    # TODO: figure out how to support editing networks. This is a read-only viewset
    # for now.

    queryset = (
        Network.objects.all()
        .prefetch_related("vlans__buildings")
        .select_related("changed_by", "shared_network")
    )
    serializer_class = NetworkSerializer
    # Only admins should have access to network data
    permission_classes = [base_permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    pagination_class = APIPagination
    filterset_class = NetworkFilter

    # The primary key is the network CIDR, so yay, we get to use regex to parse an IP address
    lookup_value_regex = r"(?:(?:25[0-5]|2[0-4]\d|[01]?\d{1,2})\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d{1,2})\/(?:3[0-2]|[0-2]?\d)"

    ordering_fields = ["network", "name", "changed"]

    @action(
        detail=True,
        methods=["get"],
        queryset=Address.objects.all()
        .select_related("host")
        .annotate(host_mac=F("host"), host_name=F("host__hostname")),
        serializer_class=AddressSerializer,
        filterset_class=AddressFilterSet,
        ordering_fields=["address", "changed"],
    )
    def addresses(self, request, pk=None):
        """Return all addresses in a given network."""
        network = Network.objects.get(network=pk)
        addresses = self.get_queryset().filter(network=network)
        paginated = self.paginate_queryset(addresses)
        serializer = self.get_serializer(paginated, many=True)
        return self.get_paginated_response(serializer.data)


class AddressPoolViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint that allows address pools to be viewed"""

    queryset = Pool.objects.all().select_related("dhcp_group")
    serializer_class = PoolSerializer
    # Only admins should have access to network data
    permission_classes = [base_permissions.IsAdminUser]
    # No need for filters, there are only a few pools
    filter_backends = [OrderingFilter]
    ordering_fields = ["name", "changed"]
    pagination_class = APIPagination


class DhcpGroupViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint that allows DHCP groups to be viewed"""

    queryset = DhcpGroup.objects.all()
    serializer_class = DhcpGroupSerializer
    # Only admins should have access to network data
    permission_classes = [base_permissions.IsAdminUser]
    filter_backends = [OrderingFilter]
    ordering_fields = ["name", "changed"]
    pagination_class = APIPagination
