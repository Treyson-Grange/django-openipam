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

from openipam.hosts.models import Host, GulRecentArpBymac, User
from openipam.dns.models import DnsRecord

from openipam.conf.ipam_settings import CONFIG_DEFAULTS

from guardian.models import UserObjectPermission, GroupObjectPermission
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from ..serializers.report import (
    GulRecentArpBymacSerializer,
    DNSReportSerializer,
    HostReportSerializer,
    DnsRecordSerializer,
    RecentStatsSerializer,
)
from datetime import datetime
from django.core.cache import cache
from django.db.models import Count
from rest_framework import permissions
from rest_framework.response import Response
from qsstats import QuerySetStats


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


class ExpiredHostsViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, base_permissions.IsAdminUser]
    serializer_class = HostReportSerializer
    pagination_class = APIPagination
    queryset = Host.objects.none()

    def get_queryset(self):
        return (
            Host.objects.select_related("mac_history")
            .filter(
                pools__isnull=False,
                expires__lte=timezone.now()
                - timedelta(
                    weeks=CONFIG_DEFAULTS["STATIC_HOST_EXPIRY_THRESHOLD_WEEKS"]
                ),
                mac_history__host__isnull=True,
            )
            .order_by("-expires")
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class OrphanedDNSViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, base_permissions.IsAdminUser]
    serializer_class = DnsRecordSerializer
    pagination_class = APIPagination
    queryset = DnsRecord.objects.select_related(
        "dns_type", "ip_content", "changed_by"
    ).filter(host__isnull=True, dns_type__name="A")


class RecentStatsViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = RecentStatsSerializer
    queryset = Host.objects.none()

    def get_cached_stats(self, queryset, date_field, cache_prefix, aggregate=None):
        stats = QuerySetStats(
            queryset, date_field, aggregate=aggregate, today=datetime.now()
        )
        today_cache_key = f"{cache_prefix}_today"
        week_cache_key = f"{cache_prefix}_week"
        month_cache_key = f"{cache_prefix}_month"

        today_stats = cache.get(today_cache_key)
        week_stats = cache.get(week_cache_key)
        month_stats = cache.get(month_cache_key)

        if today_stats is None:
            today_stats = stats.this_day()
            cache.set(today_cache_key, today_stats)
        if week_stats is None:
            week_stats = stats.this_week()
            cache.set(week_cache_key, week_stats)
        if month_stats is None:
            month_stats = stats.this_month()
            cache.set(month_cache_key, month_stats)

        return today_stats, week_stats, month_stats

    def list(self, request):
        hosts_today, hosts_week, hosts_month = self.get_cached_stats(
            Host.objects.all(), "changed", "hosts", aggregate=Count("mac")
        )
        users_today, users_week, users_month = self.get_cached_stats(
            User.objects.all(), "date_joined", "users"
        )
        dns_today, dns_week, dns_month = self.get_cached_stats(
            DnsRecord.objects.all(), "changed", "dns"
        )

        data = {
            "hosts_today": hosts_today,
            "hosts_week": hosts_week,
            "hosts_month": hosts_month,
            "users_today": users_today,
            "users_week": users_week,
            "users_month": users_month,
            "dns_today": dns_today,
            "dns_week": dns_week,
            "dns_month": dns_month,
        }

        serializer = self.get_serializer(data)
        return Response(serializer.data)
