from rest_framework.generics import ListAPIView
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION

from ..filters.admin import LogEntryFilterSet
from ..filters.base import FieldChoiceFilter

from .base import LogsPagination
from ..serializers.admin import (
    LogEntrySerializer,
    EmailLogSerializer,
    DNSLogSerializer,
    HostLogsSerializer,
    AddressLogsSerializer,
    UserLogsSerializer,
)
from openipam.log.models import EmailLog, DnsRecordsLog, HostLog, AddressLog, UserLog
from ..permissions import APIAdminPermission
from django_filters.rest_framework import DjangoFilterBackend


class LogEntryList(ListAPIView):
    permission_classes = [APIAdminPermission]
    queryset = LogEntry.objects.all().order_by("-action_time")

    serializer_class = LogEntrySerializer
    pagination_class = LogsPagination
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


class EmailLogsList(ListAPIView):
    permission_classes = [APIAdminPermission]
    queryset = EmailLog.objects.all().order_by("-when")
    serializer_class = EmailLogSerializer
    pagination_class = LogsPagination


class DNSLogsList(ListAPIView):
    permission_classes = [APIAdminPermission]
    queryset = DnsRecordsLog.objects.all()
    serializer_class = DNSLogSerializer
    pagination_class = LogsPagination


class HostLogsList(ListAPIView):
    permission_classes = [APIAdminPermission]
    queryset = HostLog.objects.all()
    serializer_class = HostLogsSerializer
    pagination_class = LogsPagination


class AddressLogsList(ListAPIView):
    permission_classes = [APIAdminPermission]
    queryset = AddressLog.objects.all()
    serializer_class = AddressLogsSerializer
    pagination_class = LogsPagination


class UserLogsList(ListAPIView):
    permission_classes = [APIAdminPermission]
    queryset = UserLog.objects.all()
    serializer_class = UserLogsSerializer
    pagination_class = LogsPagination
