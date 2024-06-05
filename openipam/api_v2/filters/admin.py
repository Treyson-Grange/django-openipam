from django_filters import rest_framework as filters
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from openipam.log.models import EmailLog, DnsRecordsLog, HostLog, AddressLog, UserLog


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
