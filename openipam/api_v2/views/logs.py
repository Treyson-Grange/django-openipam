from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.request import Request
from django.contrib.admin.models import LogEntry
from django_filters.rest_framework import DjangoFilterBackend
from .base import APIModelViewSet, APIPagination
from django_filters.rest_framework import DjangoFilterBackend
from ..filters.admin import LogEntryFilterSet, EmailLogFilterSet
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
    serializer_class = LogEntrySerializer
    permission_classes = [APIAdminPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_class = LogEntryFilterSet

    def get_queryset(self):
        queryset = super().get_queryset()
        to = self.request.query_params.get("to", None)
        if to:
            queryset = queryset.filter(to=to)
        return queryset

    def get_serializer_class(self):
        return self.serializer_class

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
        email_logs = self.filter_queryset(self.get_queryset())
        pagination = APIPagination()
        page = pagination.paginate_queryset(email_logs, request)
        dns_serializer = self.get_serializer(page, many=True)
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
