from rest_framework import serializers
from openipam.hosts.models import GulRecentArpBymac
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
