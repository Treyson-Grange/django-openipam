from django.db.models.query import QuerySet
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from openipam.network.models import DhcpGroup, Pool

from guardian.shortcuts import get_objects_for_user, get_objects_for_group, get_users_with_perms

from netfields import NetManager
from netfields.managers import NetWhere, NetQuery

from datetime import timedelta

import operator

User = get_user_model()


class HostMixin(object):
    def by_owner(self, user, use_groups=False, ids_only=False):

        # Temporarily set superuser to false so we can get only permission relations
        perm_user = User.objects.get(pk=user.pk)
        perm_user.is_superuser = False

        hosts = get_objects_for_user(perm_user, 'hosts.is_owner_host', use_groups=use_groups)

        if ids_only:
            return tuple([host.pk for host in hosts])
        else:
            return self.filter(pk__in=[host.pk for host in hosts])

    def by_group(self, group):
        hosts = get_objects_for_group(group, 'hosts.is_owner_host')
        return self.filter(pk__in=[host.pk for host in hosts])

    def by_change_perms(self, user, pk=None, ids_only=False):
        # If global permission set, then return all.
        if user.has_perm('hosts.change_host') or user.has_perm('hosts.is_owner_host'):
            if pk:
                qs = self.filter(pk=pk)
                return qs[0] if qs else None
            else:
                return self.all()
        else:
            host_perms = get_objects_for_user(user, ['hosts.is_owner_host', 'hosts.change_host'], any_perm=True).values_list('mac', flat=True)
            domain_perms = get_objects_for_user(user, ['dns.is_owner_domain', 'dns.change_domain'], any_perm=True).values_list('name', flat=True)
            network_perms = get_objects_for_user(user, ['network.is_owner_network', 'network.change_network'], any_perm=True).values_list('network', flat=True)

            qs = self.filter(
                Q(mac__in=host_perms) |
                Q(addresses__network__in=network_perms)
            )

            domain_q_list = [Q(hostname__endswith=name) for name in domain_perms]
            if domain_q_list:
                domain_qs = self.filter(reduce(operator.or_, domain_q_list))
                qs = qs | domain_qs

            if pk:
                qs = qs.filter(pk=pk).first()

            if ids_only:
                return tuple([host.pk for host in qs])
            else:
                return qs

    def expiring(self):
        host_macs = self.raw('''
            SELECT DISTINCT h.mac, h.hostname, h.expires, h.description, n.notification
            FROM hosts h
                INNER JOIN notifications_to_hosts nh ON (h.mac = nh.mac)
                INNER JOIN notifications n ON (n.id = nh.nid)
                INNER JOIN addresses a ON (h.mac = a.mac)
                WHERE (h.expires - n.notification) <= now()
        ''')
        host_macs = [host.mac for host in host_macs]
        hosts = self.filter(mac__in=host_macs)
        return hosts

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None



class HostQuerySet(QuerySet, HostMixin):
    pass


class HostManager(NetManager):

    def __getattr__(self, name):
        return getattr(self.get_query_set(), name)

    def get_query_set(self):
        q = NetQuery(self.model, NetWhere)
        return HostQuerySet(self.model, q)

    def get_owners(self, mac):
        host = self.get(mac=mac)
        owners = get_users_with_perms(host, attach_perms=True, with_group_users=False)
        owners = [k for k, v in owners.items() if 'is_owner_host' in v]
        return owners

    #TODO!  Finish this and use it for everthing except the web form
    def add_or_update_host(self, user, hostname=None, mac=None, expire_days=None, description=None, dhcp_group=None,
                           pool=None, ip_addresses=None, network=None, user_owners=None, group_owners=None, instance=None):

        if isinstance(user, str):
            user = User.objects.get(username=user)

        if not instance:
            instance = self.model()

        # Set mac address
        instance.set_mac_address(mac)

        instance.user = instance.changed_by = user

        instance.hostname = hostname
        instance.description = description

        if expire_days:
            instance.expire_days = expire_days
            instance.exipires = instance.set_expiration(timedelta(int(expire_days)))

        if isinstance(dhcp_group, str):
            dhcp_group = DhcpGroup.objects.get(name=dhcp_group)
        instance.dhcp_group = dhcp_group

        if pool:
            if isinstance(pool, int):
                pool = Pool.objects.get(name=pool)
            instance.pool = pool

        if ip_addresses:
            instance.ip_addresses = ip_addresses

        if network:
            instance.network = network

        instance.full_clean()
        instance.save()

        if instance.pool or instance.network or instance.ip_addresses:
            instance.set_network_ip_or_pool()

            instance.address_type_id = instance.address_type
            instance.save()

        user_groups = []

        if user_owners or group_owners:
            if isinstance(user_owners, list):
                users_to_add = User.objects.filter(username__in=[user_owner.lower() for user_owner in user_owners])
            else:
                users_to_add = User.objects.filter(username__iexact=user_owners)
            users_to_add = list(users_to_add)
            user_groups += users_to_add

            if isinstance(group_owners, list):
                groups_to_add = Group.objects.filter(name__in=group_owners)
            else:
                groups_to_add = Group.objects.filter(name=group_owners)
            groups_to_add = list(groups_to_add)
            user_groups += groups_to_add

            instance.remove_owners()
            for user_group in user_groups:
                instance.assign_owner(user_group)
        else:
            has_users, has_groups = instance.get_owners()
            if not has_users and not has_groups:
                instance.assign_owner(user)

        return instance
