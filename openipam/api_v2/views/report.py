from rest_framework.response import Response
from rest_framework import status
from ..permissions import APIAdminPermission
from .base import APIPagination
from rest_framework.viewsets import ReadOnlyModelViewSet
from ..serializers.hosts import HostSerializer
from ..serializers.dns import DNSSerializer
from rest_framework.renderers import (
    JSONRenderer,
    BrowsableAPIRenderer,
)
from rest_framework import permissions as base_permissions

from rest_framework_csv.renderers import CSVRenderer
from django.contrib.contenttypes.models import ContentType
from django.db.models import F

from openipam.hosts.models import Host, GulRecentArpBymac
from openipam.dns.models import DnsRecord

from openipam.conf.ipam_settings import CONFIG_DEFAULTS

from guardian.models import UserObjectPermission, GroupObjectPermission
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from ..serializers.report import GulRecentArpBymacSerializer, DNSReportSerializer


class ExposedHostCSVRenderer(CSVRenderer):
    header = [
        "hostname",
        "mac",
        "description",
        "master_ip_address",
        "user_owners",
        "group_owners",
    ]


class ExposedHostViewSet(ReadOnlyModelViewSet):
    permission_classes = [APIAdminPermission]
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer, ExposedHostCSVRenderer)
    queryset = Host.objects.all()
    pagination_class = APIPagination
    serializer_class = HostSerializer

    def list(self, request, format=None):
        hosts = (
            Host.objects.prefetch_related("addresses")
            .filter(
                structured_attributes__structured_attribute_value__attribute__name="nac-profile",
                structured_attributes__structured_attribute_value__value__startswith=CONFIG_DEFAULTS[
                    "NAC_PROFILE_IS_SERVER_PREFIX"
                ],
            )
            .annotate(
                nac_profile=F(
                    "structured_attributes__structured_attribute_value__value"
                ),
            )
        )
        user_perms_prefetch = UserObjectPermission.objects.select_related(
            "permission", "user"
        ).filter(
            content_type=ContentType.objects.get_for_model(Host),
            object_pk__in=[str(host.mac) for host in hosts],
            permission__codename="is_owner_host",
        )
        group_perms_prefetch = GroupObjectPermission.objects.select_related(
            "permission", "group"
        ).filter(
            content_type=ContentType.objects.get_for_model(Host),
            object_pk__in=[str(host.mac) for host in hosts],
            permission__codename="is_owner_host",
        )
        data = []
        for host in hosts:
            owners = host.get_owners(
                name_only=True,
                user_perms_prefetch=user_perms_prefetch,
                group_perms_prefetch=group_perms_prefetch,
            )
            data.append(
                {
                    "hostname": host.hostname,
                    "mac": str(host.mac),
                    "description": host.description,
                    "master_ip_address": (
                        host.ip_addresses[0] if host.ip_addresses else None
                    ),
                    "user_owners": ", ".join(owners[0]),
                    "group_owners": ", ".join(owners[1]),
                    "nac_profile": host.nac_profile,
                }
            )
        page = self.paginate_queryset(data)
        if page is not None:
            return self.get_paginated_response(page)

        if request.accepted_renderer.format == "json":
            return Response({"data": data}, status=status.HTTP_200_OK)
        else:
            return Response(data, status=status.HTTP_200_OK)


class DisabledHostsViewSet(ReadOnlyModelViewSet):
    queryset = GulRecentArpBymac.objects.none()
    serializer_class = GulRecentArpBymacSerializer
    permission_classes = [IsAuthenticated, base_permissions.IsAdminUser]
    pagination_class = APIPagination

    def get_queryset(self):
        return (
            GulRecentArpBymac.objects.select_related("host")
            .filter(stopstamp__gt=timezone.now() - timedelta(minutes=10))
            .exclude(host__leases__ends__lt=timezone.now())
            .extra(
                where=[
                    "gul_recent_arp_bymac.mac IN (SELECT mac from disabled)",
                ]
            )
        )


class HostDNSViewSet(ReadOnlyModelViewSet):
    queryset = Host.objects.none()
    serializer_class = HostSerializer
    permission_classes = [IsAuthenticated, base_permissions.IsAdminUser]
    pagination_class = APIPagination

    def get_queryset(self):
        return Host.objects.filter(
            dns_records__isnull=True,
            addresses__isnull=False,
            expires__gte=timezone.now(),
        )


class PTRDNSViewSet(ReadOnlyModelViewSet):
    queryset = DnsRecord.objects.none()
    serializer_class = DNSReportSerializer
    permission_classes = [IsAuthenticated, base_permissions.IsAdminUser]
    pagination_class = APIPagination

    def get_queryset(self):
        return DnsRecord.objects.raw(
            r"""
            SELECT d.*, a.address as address, d3.name as arecord, a.mac as arecord_host
            FROM dns_records AS d
                LEFT JOIN addresses AS a ON (
                    regexp_replace(d.name, '([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)..*', E'\\4.\\3.\\2.\\1')::inet = a.address
                )
                LEFT JOIN dns_records AS d2 ON (
                    d2.name = d.text_content AND d2.ip_content IS NOT NULL
                )
                LEFT JOIN dns_records AS d3 ON (
                    a.address = d3.ip_content
                )
            WHERE d.tid = '12'
                AND d.name LIKE '%%.in-addr.arpa'
                AND d2.ip_content IS NULL

            ORDER BY d.changed DESC
                --AND d.text_content != d2.name
        """
        )
