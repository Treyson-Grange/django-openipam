from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from rest_framework import serializers
from openipam.log.models import EmailLog, DnsRecordsLog, HostLog, AddressLog, UserLog


class LogEntrySerializer(serializers.ModelSerializer):
    content_type = serializers.SlugRelatedField(read_only=True, slug_field="model")
    action_flag = serializers.SerializerMethodField()

    def get_action_flag(self, obj: LogEntry):
        if obj.action_flag == ADDITION:
            return "Addition"
        elif obj.action_flag == CHANGE:
            return "Change"
        elif obj.action_flag == DELETION:
            return "Deletion"
        else:
            # this shouldn't happen, but just in case
            return obj.action_flag

    class Meta:
        model = LogEntry
        fields = "__all__"


class EmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailLog
        fields = "__all__"


class DNSLogSerializer(serializers.ModelSerializer):
    dns_type = serializers.SerializerMethodField()
    changed_by = serializers.SerializerMethodField()
    changed_by_url = serializers.SerializerMethodField()

    def get_dns_type(self, obj: DnsRecordsLog):
        return obj.dns_type.name

    def get_changed_by(self, obj: DnsRecordsLog):
        return f"%s %s (%s)" % (
            obj.changed_by.first_name,
            obj.changed_by.last_name,
            obj.changed_by.username,
        )

    def get_changed_by_url(self, obj: DnsRecordsLog):
        return f"/users/{obj.changed_by.username}/"

    class Meta:
        model = DnsRecordsLog
        fields = [
            "name",
            "ttl",
            "dns_type",
            "priority",
            "ip_content",
            "changed",
            "changed_by",
            "changed_by_url",
        ]


class HostLogsSerializer(serializers.ModelSerializer):
    changed_by = serializers.SerializerMethodField()
    changed_by_url = serializers.SerializerMethodField()

    def get_changed_by(self, obj: HostLog):
        return f"%s %s (%s)" % (
            obj.changed_by.first_name,
            obj.changed_by.last_name,
            obj.changed_by.username,
        )

    def get_changed_by_url(self, obj: HostLog):
        return f"/users/{obj.changed_by.username}/"

    class Meta:
        model = HostLog
        fields = ["mac", "hostname", "changed", "changed_by", "changed_by_url"]


class AddressLogsSerializer(serializers.ModelSerializer):

    class Meta:
        model = AddressLog
        fields = [
            "address",
            "mac",
            "pool",
            "reserved",
            "network",
            "changed",
            "changed_by",
        ]


class UserLogsSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    is_ipam_admin = serializers.SerializerMethodField()

    def get_full_name(self, obj: UserLog):
        return f"{obj.first_name} {obj.last_name}"

    def get_is_ipam_admin(self, obj: UserLog):
        return obj.is_ipamadmin

    class Meta:
        model = UserLog
        fields = [
            "username",
            "full_name",
            "email",
            "is_staff",
            "is_superuser",
            "is_ipam_admin",
            "source_id",
            "last_login",
        ]
