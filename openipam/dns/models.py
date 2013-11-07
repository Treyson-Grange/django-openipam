from django.db import models
from django.core.exceptions import ValidationError

from openipam.dns.managers import DnsManager

from guardian.models import UserObjectPermissionBase, GroupObjectPermissionBase


class DomainManager(models.Manager):
    pass


class Domain(models.Model):
    name = models.CharField(max_length=255, unique=True)
    master = models.CharField(max_length=128, blank=True, null=True, default=None)
    last_check = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=6)
    notified_serial = models.IntegerField(blank=True, null=True)
    account = models.CharField(max_length=40, blank=True, null=True, default=None)
    description = models.TextField(blank=True, null=True)
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey('user.User', db_column='changed_by')

    objects = DomainManager()

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'domains'
        permissions = (
            ('is_owner_domain', 'Is owner'),
            ('add_records_to_domain', 'Can add records to'),
        )


class DomainUserObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey('Domain', related_name='user_permissions')

    class Meta:
        verbose_name = 'Domain User Permission'


class DomainGroupObjectPermission(GroupObjectPermissionBase):
    content_object = models.ForeignKey('Domain', related_name='group_permissions')

    class Meta:
        verbose_name = 'Domain Group Permission'


class DnsRecord(models.Model):
    domain = models.ForeignKey('Domain', db_column='did', verbose_name='Domain')
    dns_type = models.ForeignKey('DnsType', db_column='tid', verbose_name='Type')
    dns_view = models.ForeignKey('DnsView', db_column='vid', verbose_name='View', blank=True, null=True)
    name = models.CharField(max_length=255)
    text_content = models.CharField(max_length=255, blank=True, null=True)
    address = models.ForeignKey('network.Address', db_column='ip_content', verbose_name='IP Content', blank=True, null=True)
    ttl = models.IntegerField(default=86400, blank=True, null=True)
    priority = models.IntegerField(verbose_name='Priority', blank=True, null=True)
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey('user.User', db_column='changed_by')

    objects = DnsManager()

    def __unicode__(self):
        return self.name

    def clean(self):
        # Make sure these are saved as NULL to db.
        if not self.text_content:
            self.text_content = None
        if not self.ip_content:
            self.ip_content = None

        if self.text_content and self.ip_content:
            raise ValidationError('Text Content and IP Content cannot both exist for %s' % self.name)

    class Meta:
        db_table = 'dns_records'
        ordering = ('dns_type', 'name')
        verbose_name = 'DNS Record'



class DnsRecordMunged(models.Model):
    domain_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=32, blank=True)
    content = models.TextField(blank=True)
    ttl = models.IntegerField(null=True, blank=True)
    prio = models.IntegerField(null=True, blank=True)
    change_date = models.IntegerField(null=True, blank=True)
    view_id = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'dns_records_munged'


class DhcpDnsRecord(models.Model):
    did = models.ForeignKey('Domain', db_column='did')
    name = models.ForeignKey('hosts.Host', unique=True, db_column='name')
    ip_content = models.ForeignKey('network.Address', null=True, db_column='ip_content', blank=True)
    ttl = models.IntegerField(default=-1, blank=True, null=True)
    changed = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'dhcp_dns_records'


class DnsType(models.Model):
    name = models.CharField(max_length=16, blank=True)
    description = models.TextField(blank=True, null=True)
    min_permissions = models.ForeignKey('user.Permission', db_column='min_permissions')

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'dns_types'
        permissions = (
            ('add_records_to_dnstype', 'Can add records to'),
        )
        ordering = ('name',)
        verbose_name = 'DNS Type'


class DnsTypeUserObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey('DnsType', related_name='user_permissions')


class DnsTypeGroupObjectPermission(GroupObjectPermissionBase):
    content_object = models.ForeignKey('DnsType', related_name='group_permissions')


class DnsView(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'dns_views'


class Supermaster(models.Model):
    ip = models.CharField(max_length=25)
    nameserver = models.CharField(max_length=255)
    account = models.CharField(max_length=40, blank=True, null=True, default=None)
    changed = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey('user.User', db_column='changed_by')

    def __unicode__(self):
        return self.ip

    class Meta:
        db_table = 'supermasters'


class PdnsZoneXfer(models.Model):
    domain = models.ForeignKey('Domain')
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10)
    content = models.CharField(max_length=255)
    ttl = models.IntegerField(null=True, blank=True)
    priority = models.IntegerField(null=True, blank=True)
    change_date = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'pdns_zone_xfer'


class Record(models.Model):
    domain_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=32, blank=True)
    content = models.TextField(blank=True)
    ttl = models.IntegerField(null=True, blank=True)
    prio = models.IntegerField(null=True, blank=True)
    change_date = models.IntegerField(null=True, blank=True)
    view_id = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return '%s %s' % (self.id, self.name)

    class Meta:
        managed = False
        db_table = 'records'


class RecordMunged(models.Model):
    domain_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    ttl = models.IntegerField(null=True, blank=True)
    prio = models.IntegerField(null=True, blank=True)
    change_date = models.IntegerField(null=True, blank=True)
    view_id = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return '%s %s' % (self.id, self.name)

    class Meta:
        managed = False
        db_table = 'records_munged'

