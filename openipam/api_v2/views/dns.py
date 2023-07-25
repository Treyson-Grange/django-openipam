"""DNS API Views."""

from openipam.dns.models import DnsRecord, Domain
from ..serializers.dns import DNSSerializer, DomainSerializer, DNSCreateSerializer, DomainCreateSerializer
from rest_framework import permissions
from .base import APIModelViewSet
from ..filters.dns import DnsFilter, DomainFilter
from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.db.utils import DataError


class DnsViewSet(APIModelViewSet):
    """API endpoint that allows dns records to be viewed or edited."""

    queryset = DnsRecord.objects.select_related("ip_content", "dns_type", "host").all()
    serializer_class = DNSSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterFields = ["name", "ip_content", "text_content", "dns_type"]
    filterClass = DnsFilter

    def create(self, request, *args, **kwargs):
        """Create a new DNS record."""
        try:
            serializer = DNSCreateSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=False)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (ValidationError, DataError) as e:
            error_list = []
            if hasattr(e, "error_dict"):
                for key, errors in list(e.message_dict.items()):
                    for error in errors:
                        error_list.append("%s: %s" % (key.capitalize(), error))
            else:
                error_list.append(e.message)
            return Response(
                {"non_field_errors": error_list}, status=status.HTTP_400_BAD_REQUEST
            )


class DomainViewSet(APIModelViewSet):
    queryset = Domain.objects.select_related().all()
    serializer_class = DomainSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterFields = ("name", "username")
    filter_class = DomainFilter

    def create(self, request, *args, **kwargs):
        serializer = DomainCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        try:
            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            return response
        except (ValidationError, DataError) as e:
            error_list = []
            if hasattr(e, "error_dict"):
                for key, errors in list(e.message_dict.items()):
                    for error in errors:
                        error_list.append("%s: %s" % (key.capitalize(), error))
            else:
                error_list.append(e.message)
            return Response(
                {"non_field_errors": error_list}, status=status.HTTP_400_BAD_REQUEST
            )
