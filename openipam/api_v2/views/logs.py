from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.request import Request
from django.contrib.admin.models import LogEntry
from django_filters.rest_framework import DjangoFilterBackend
from .base import APIModelViewSet, APIPagination
from django_filters.rest_framework import DjangoFilterBackend
from ..filters.admin import LogEntryFilterSet
from ..filters.base import FieldChoiceFilter
from ..permissions import APIAdminPermission
from openipam.log.models import EmailLog, DnsRecordsLog, HostLog, AddressLog, UserLog
from django.contrib.admin.models import LogEntry
from ..serializers.admin import (
    LogEntrySerializer,
    EmailLogSerializer,
    DNSLogSerializer,
    HostLogsSerializer,
    AddressLogsSerializer,
    UserLogsSerializer,
)


class LogViewSet(APIModelViewSet):
    """API endpoint that allows logs to be viewed"""

    queryset = LogEntry.objects.all().order_by("-action_time")
    lookup_field = "id"
    serializer_class = LogEntrySerializer
    permission_classes = [APIAdminPermission]
    filter_backends = [FieldChoiceFilter, DjangoFilterBackend]
    filterset_class = LogEntryFilterSet
    filter_field = "content_type__model"
    filter_query_prefix = "include"
    filter_choices = [
        "host",
        "dnsrecord",
        "address",
        "user",
        "group",
        "domain",
    ]
    filter_allow_unlisted = True

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related("content_type").prefetch_related("user")
        return queryset

    def get_serializer_class(self):
        return LogEntrySerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    @action(detail=False, methods=["get"])
    def host(self, request: Request):
        """List all host logs."""
        queryset = HostLog.objects.all()
        pagination = APIPagination()
        page = pagination.paginate_queryset(queryset, request)
        host_serializer = HostLogsSerializer(page, many=True)
        return pagination.get_paginated_response(host_serializer.data)

    @action(detail=False, methods=["get"])
    def email(self, request: Request):
        """List all email logs."""
        queryset = EmailLog.objects.all().order_by("-when")
        pagination = APIPagination()
        page = pagination.paginate_queryset(queryset, request)
        dns_serializer = EmailLogSerializer(page, many=True)
        return pagination.get_paginated_response(dns_serializer.data)

    @action(detail=False, methods=["get"])
    def dns(self, request: Request):
        """List all DNS logs."""
        queryset = DnsRecordsLog.objects.all()
        pagination = APIPagination()
        page = pagination.paginate_queryset(queryset, request)
        dns_serializer = DNSLogSerializer(page, many=True)
        return pagination.get_paginated_response(dns_serializer.data)

    @action(detail=False, methods=["get"])
    def address(self, request: Request):
        """List all address logs."""
        queryset = AddressLog.objects.all()
        pagination = APIPagination()
        page = pagination.paginate_queryset(queryset, request)
        address_serializer = AddressLogsSerializer(page, many=True)
        return pagination.get_paginated_response(address_serializer.data)

    @action(detail=False, methods=["get"])
    def user(self, request: Request):
        """List all user logs."""
        queryset = UserLog.objects.all()
        pagination = APIPagination()
        page = pagination.paginate_queryset(queryset, request)
        user_serializer = UserLogsSerializer(page, many=True)
        return pagination.get_paginated_response(user_serializer.data)
