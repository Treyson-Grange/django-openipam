"""Miscellaneous views that don't really fit anywhere else."""

from rest_framework import status, viewsets as lib_viewsets
from rest_framework.views import APIView
from ..serializers.misc import AttributeSerializer, StructuredAttributeValueSerializer
from openipam.hosts.models import Attribute, StructuredAttributeValue
from django.db.models import Prefetch
from openipam.network.models import Network, Lease, Address
from openipam.hosts.models import Host
from django.utils import timezone
from openipam.dns.models import DnsRecord
from functools import reduce
import operator
from datetime import timedelta
from django.db.models import Q
from rest_framework.response import Response
from collections import OrderedDict
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from .base import APIPagination


User = get_user_model()


class AttributeViewSet(lib_viewsets.ReadOnlyModelViewSet):
    """API endpoint that allows attributes to be viewed or edited."""

    queryset = (
        Attribute.objects.select_related("changed_by")
        .prefetch_related(
            Prefetch(
                "choices",
                queryset=StructuredAttributeValue.objects.select_related("changed_by"),
            )
        )
        .all()
    )
    serializer_class = AttributeSerializer

    @action(detail=False, url_path="structured-values")
    def structured_values(self, request, *args, **kwargs):
        queryset = StructuredAttributeValue.objects.select_related(
            "attribute", "changed_by"
        ).all()
        serializer = StructuredAttributeValueSerializer(queryset, many=True)
        return Response(serializer.data)


class DashboardAPIView(APIView):
    def get(self, request, format=None, **kwargs):
        wireless_networks = Network.objects.filter(
            dhcp_group__name__in=["aruba_wireless", "aruba_wireless_eastern"]
        )
        wireless_networks_available_qs = [
            Q(address__net_contained=network.network) for network in wireless_networks
        ]

        data = {
            "all_hosts": {
                "count": Host.objects.all().count(),
            },
            "expired_hosts": {
                "count": Host.objects.filter(expires__lte=timezone.now()).count(),
            },
            "static_hosts": {
                "count": Host.objects.filter(
                    addresses__isnull=False, expires__gte=timezone.now()
                ).count(),
            },
            "dynamic_hosts": {
                "count": Host.objects.filter(
                    pools__isnull=True, expires__gte=timezone.now()
                ).count(),
            },
            "active_leases": {
                "count": Lease.objects.filter(ends__gte=timezone.now()).count(),
            },
            "abandoned_leases": {
                "count": Lease.objects.filter(abandoned=True).count(),
            },
            "networks_total": {
                "count": Network.objects.all().count(),
                "wireless_count": wireless_networks.count(),
            },
            "available_wireless_addresses": {
                "count": Address.objects.filter(
                    reduce(operator.or_, wireless_networks_available_qs),
                    leases__ends__lt=timezone.now(),
                ).count(),
            },
            "dns_a_records": {
                "count": DnsRecord.objects.filter(
                    dns_type__name__in=["A", "AAAA"]
                ).count(),
            },
            "dns_cname_records": {
                "count": DnsRecord.objects.filter(dns_type__name="CNAME").count(),
            },
            "dns_mx_records": {
                "count": DnsRecord.objects.filter(dns_type__name="MX").count(),
            },
            "active_users_within_1_year": {
                "count": User.objects.filter(
                    last_login__gte=(timezone.now() - timedelta(days=365))
                ).count(),
            },
        }

        return Response(data, status=status.HTTP_200_OK)
