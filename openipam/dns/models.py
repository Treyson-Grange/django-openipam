from django.db import models


class Domain(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    master = models.CharField(max_length=128, blank=True)
    last_check = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=6)
    notified_serial = models.IntegerField(null=True, blank=True)
    account = models.CharField(max_length=40, blank=True)
    description = models.TextField(blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('group.User', db_column='changed_by')
    class Meta:
        db_table = 'domains'


class DnsRecord(models.Model):
    id = models.IntegerField(primary_key=True)
    did = models.ForeignKey('Domain', db_column='did')
    tid = models.ForeignKey('DnsType', db_column='tid')
    vid = models.ForeignKey('DnsView', null=True, db_column='vid', blank=True)
    name = models.CharField(max_length=255)
    text_content = models.CharField(max_length=255, blank=True)
    ip_content = models.ForeignKey('network.Address', null=True, db_column='ip_content', blank=True)
    ttl = models.IntegerField(null=True, blank=True)
    priority = models.IntegerField(null=True, blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('group.User', db_column='changed_by')
    class Meta:
        db_table = 'dns_records'


class DnsRecordMunged(models.Model):
    domain_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=32, blank=True)
    content = models.TextField(blank=True)
    ttl = models.IntegerField(null=True, blank=True)
    prio = models.IntegerField(null=True, blank=True)
    change_date = models.IntegerField(null=True, blank=True)
    view_id = models.IntegerField(null=True, blank=True)
    class Meta:
        managed = False
        db_table = 'dns_records_munged'


class DhcpDnsRecord(models.Model):
    id = models.IntegerField(primary_key=True)
    did = models.ForeignKey('Domain', db_column='did')
    name = models.ForeignKey('host.Host', unique=True, db_column='name')
    ip_content = models.ForeignKey('network.Address', null=True, db_column='ip_content', blank=True)
    ttl = models.IntegerField(null=True, blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = 'dhcp_dns_records'


class DnsType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=16, blank=True)
    description = models.TextField(blank=True)
    min_permissions = models.ForeignKey('group.Permission', db_column='min_permissions')
    class Meta:
        db_table = 'dns_types'


class DnsView(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True)
    class Meta:
        db_table = 'dns_views'


class Supermaster(models.Model):
    id = models.IntegerField(primary_key=True)
    ip = models.CharField(max_length=25)
    nameserver = models.CharField(max_length=255)
    account = models.CharField(max_length=40, blank=True)
    changed = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey('group.User', db_column='changed_by')
    class Meta:
        db_table = 'supermasters'


class PdnsZoneXfer(models.Model):
    id = models.IntegerField(primary_key=True)
    domain = models.ForeignKey('Domain')
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10)
    content = models.CharField(max_length=255)
    ttl = models.IntegerField(null=True, blank=True)
    priority = models.IntegerField(null=True, blank=True)
    change_date = models.IntegerField(null=True, blank=True)
    class Meta:
        managed = False
        db_table = 'pdns_zone_xfer'


class Record(models.Model):
    id = models.IntegerField(primary_key=True)
    domain_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=32, blank=True)
    content = models.TextField(blank=True)
    ttl = models.IntegerField(null=True, blank=True)
    prio = models.IntegerField(null=True, blank=True)
    change_date = models.IntegerField(null=True, blank=True)
    view_id = models.IntegerField(null=True, blank=True)
    class Meta:
        managed = False
        db_table = 'records'


class RecordMunged(models.Model):
    id = models.IntegerField(primary_key=True)
    domain_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    ttl = models.IntegerField(null=True, blank=True)
    prio = models.IntegerField(null=True, blank=True)
    change_date = models.IntegerField(null=True, blank=True)
    view_id = models.IntegerField(null=True, blank=True)
    class Meta:
        managed = False
        db_table = 'records_munged'

