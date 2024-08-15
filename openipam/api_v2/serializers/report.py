from rest_framework import serializers
from openipam.hosts.models import GulRecentArpBymac
from openipam.hosts.models import Host
from openipam.dns.models import DnsRecord


class GulRecentArpBymacSerializer(serializers.ModelSerializer):
    class Meta:
        model = GulRecentArpBymac
        fields = ["host", "address", "stopstamp", "objects"]


class DNSReportSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    text_content = serializers.CharField()
    ip_content = serializers.CharField()
    changed = serializers.DateTimeField()
    address = serializers.CharField()
    arecord = serializers.CharField()
    arecord_host = serializers.CharField()


class HostReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = ["hostname", "mac", "expires"]


class DnsRecordSerializer(serializers.ModelSerializer):
    ip_content = serializers.CharField()
    domain = serializers.CharField()
    changed_by = serializers.CharField()

    class Meta:
        model = DnsRecord
        fields = ["domain", "ip_content", "changed", "changed_by"]


class RecentStatsSerializer(serializers.Serializer):
    hosts_today = serializers.IntegerField()
    hosts_week = serializers.IntegerField()
    hosts_month = serializers.IntegerField()
    users_today = serializers.IntegerField()
    users_week = serializers.IntegerField()
    users_month = serializers.IntegerField()
    dns_today = serializers.IntegerField()
    dns_week = serializers.IntegerField()
    dns_month = serializers.IntegerField()
