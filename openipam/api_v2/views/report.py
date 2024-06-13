from rest_framework.response import Response
from rest_framework import status
from ..permissions import APIAdminPermission
from .base import APIModelViewSet, APIPagination
from ..serializers.hosts import HostSerializer
from rest_framework.renderers import (
    JSONRenderer,
    BrowsableAPIRenderer,
)

from rest_framework_csv.renderers import CSVRenderer
from django.contrib.contenttypes.models import ContentType
from django.db.models import F

from openipam.hosts.models import Host
from openipam.conf.ipam_settings import CONFIG_DEFAULTS

from guardian.models import UserObjectPermission, GroupObjectPermission


class ExposedHostCSVRenderer(CSVRenderer):
    header = [
        "hostname",
        "mac",
        "description",
        "master_ip_address",
        "user_owners",
        "group_owners",
    ]


class ExposedHostViewSet(APIModelViewSet):
    permission_classes = [APIAdminPermission]
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer, ExposedHostCSVRenderer)
    queryset = Host.objects.all()
    pagination_class = APIPagination
    serializer_class = HostSerializer

    def list(self, request, format=None):
        hosts = (
            Host.objects.prefetch_related("addresses")
            .filter(
                structured_attributes__structured_attribute_value__attribute__name="nac-profile",
                structured_attributes__structured_attribute_value__value__startswith=CONFIG_DEFAULTS[
                    "NAC_PROFILE_IS_SERVER_PREFIX"
                ],
            )
            .annotate(
                nac_profile=F(
                    "structured_attributes__structured_attribute_value__value"
                ),
            )
        )
        user_perms_prefetch = UserObjectPermission.objects.select_related(
            "permission", "user"
        ).filter(
            content_type=ContentType.objects.get_for_model(Host),
            object_pk__in=[str(host.mac) for host in hosts],
            permission__codename="is_owner_host",
        )
        group_perms_prefetch = GroupObjectPermission.objects.select_related(
            "permission", "group"
        ).filter(
            content_type=ContentType.objects.get_for_model(Host),
            object_pk__in=[str(host.mac) for host in hosts],
            permission__codename="is_owner_host",
        )
        data = []
        for host in hosts:
            owners = host.get_owners(
                name_only=True,
                user_perms_prefetch=user_perms_prefetch,
                group_perms_prefetch=group_perms_prefetch,
            )
            data.append(
                {
                    "hostname": host.hostname,
                    "mac": str(host.mac),
                    "description": host.description,
                    "master_ip_address": (
                        host.ip_addresses[0] if host.ip_addresses else None
                    ),
                    "user_owners": ", ".join(owners[0]),
                    "group_owners": ", ".join(owners[1]),
                    "nac_profile": host.nac_profile,
                }
            )
        page = self.paginate_queryset(data)
        if page is not None:
            return self.get_paginated_response(page)

        if request.accepted_renderer.format == "json":
            return Response({"data": data}, status=status.HTTP_200_OK)
        else:
            return Response(data, status=status.HTTP_200_OK)
