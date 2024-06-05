from django_filters import rest_framework as filters
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from openipam.log.models import EmailLog, DnsRecordsLog, HostLog, AddressLog, UserLog
from django.contrib.auth.models import Group


class LogEntryFilterSet(filters.FilterSet):
    type = filters.CharFilter(field_name="content_type__model")
    flag = filters.ChoiceFilter(
        field_name="action_flag",
        choices=[
            # TODO: change to use lowercase (this will need updating in the frontend)
            (ADDITION, "Addition"),
            (CHANGE, "Change"),
            (DELETION, "Deletion"),
        ],
    )
    user = filters.CharFilter(field_name="user__username")

    class Meta:
        model = LogEntry
        fields = ["type", "flag", "user"]


class EmailLogFilterSet(filters.FilterSet):
    to = filters.CharFilter(field_name="to")

    class Meta:
        model = EmailLog
        fields = ["to"]


class HostLogFilterSet(filters.FilterSet):
    hostname = filters.CharFilter(field_name="hostname")
    mac = filters.CharFilter(field_name="mac")

    class Meta:
        model = HostLog
        fields = ["hostname", "mac"]


class AddressLogFilterSet(filters.FilterSet):
    address = filters.CharFilter(field_name="address")
    mac = filters.CharFilter(field_name="mac")

    class Meta:
        model = AddressLog
        fields = ["address", "mac"]


class UserLogFilterSet(filters.FilterSet):
    username = filters.CharFilter(field_name="username")
    first_name = filters.CharFilter(field_name="first_name")
    last_name = filters.CharFilter(field_name="last_name")
    email = filters.CharFilter(field_name="email")
    is_staff = filters.BooleanFilter(field_name="is_staff")
    is_superuser = filters.BooleanFilter(field_name="is_superuser")

    class Meta:
        model = UserLog
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_superuser",
        ]


class DnsRecordsLogFilterSet(filters.FilterSet):
    name = filters.CharFilter(field_name="name")
    dns_type = filters.CharFilter(field_name="dns_type")
    ip_content = filters.CharFilter(field_name="ip_content")

    class Meta:
        model = DnsRecordsLog
        fields = ["name", "dns_type", "ip_content"]
