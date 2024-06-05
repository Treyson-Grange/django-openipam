from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.request import Request
from django.contrib.admin.models import LogEntry
from django_filters.rest_framework import DjangoFilterBackend
from .base import APIModelViewSet, APIPagination
from django_filters.rest_framework import DjangoFilterBackend
from ..filters.admin import (
    LogEntryFilterSet,
    EmailLogFilterSet,
    HostLogFilterSet,
    AddressLogFilterSet,
    UserLogFilterSet,
    DnsRecordsLogFilterSet,
)
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
    serializer_class = LogEntrySerializer
    permission_classes = [APIAdminPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_class = LogEntryFilterSet

    def get_serializer_class(self):
        return self.serializer_class

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    @action(
        detail=False,
        methods=["get"],
        queryset=HostLog.objects.all(),
        filter_backends=[DjangoFilterBackend],
        serializer_class=HostLogsSerializer,
        filterset_class=HostLogFilterSet,
    )
    def host(self, request: Request):
        """List all host logs with filtering."""
        queryset = HostLog.objects.all()
        queryset = self.filter_queryset(queryset)
        pagination = APIPagination()
        page = pagination.paginate_queryset(queryset, request)
        host_serializer = self.get_serializer(page, many=True)
        return pagination.get_paginated_response(host_serializer.data)

    @action(
        detail=False,
        methods=["get"],
        queryset=EmailLog.objects.all(),
        filter_backends=[DjangoFilterBackend],
        serializer_class=EmailLogSerializer,
        filterset_class=EmailLogFilterSet,
    )
    def email(self, request: Request):
        """List all email logs."""
        queryset = self.filter_queryset(EmailLog.objects.all())
        pagination = APIPagination()
        page = pagination.paginate_queryset(queryset, request)
        email_serializer = self.get_serializer(page, many=True)
        return pagination.get_paginated_response(email_serializer.data)

    @action(
        detail=False,
        methods=["get"],
        queryset=DnsRecordsLog.objects.all(),
        filter_backends=[DjangoFilterBackend],
        serializer_class=DNSLogSerializer,
        filterset_class=DnsRecordsLogFilterSet,
    )
    def dns(self, request: Request):
        """List all DNS logs."""
        queryset = self.filter_queryset(DnsRecordsLog.objects.all())
        pagination = APIPagination()
        page = pagination.paginate_queryset(queryset, request)
        dns_serializer = self.get_serializer(page, many=True)
        return pagination.get_paginated_response(dns_serializer.data)

    @action(
        detail=False,
        methods=["get"],
        queryset=AddressLog.objects.all(),
        filter_backends=[DjangoFilterBackend],
        serializer_class=AddressLogsSerializer,
        filterset_class=AddressLogFilterSet,
    )
    def address(self, request: Request):
        """List all address logs."""
        queryset = self.filter_queryset(AddressLog.objects.all())
        pagination = APIPagination()
        page = pagination.paginate_queryset(queryset, request)
        address_serializer = self.get_serializer(page, many=True)
        return pagination.get_paginated_response(address_serializer.data)

    @action(
        detail=False,
        methods=["get"],
        queryset=UserLog.objects.all(),
        filter_backends=[DjangoFilterBackend],
        serializer_class=UserLogsSerializer,
        filterset_class=UserLogFilterSet,
    )
    def user(self, request: Request):
        """List all user logs."""
        queryset = self.filter_queryset(UserLog.objects.all())
        pagination = APIPagination()
        page = pagination.paginate_queryset(queryset, request)
        user_serializer = self.get_serializer(page, many=True)
        return pagination.get_paginated_response(user_serializer.data)
