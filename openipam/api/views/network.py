from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import filters
from openipam.network.models import Network, Address, DhcpGroup
from openipam.api.serializers.network import NetworkSerializer
from django_filters import FilterSet, CharFilter


class NetworkFilter(FilterSet):
    network = CharFilter(lookup_type='net_contained_or_equal')
    name = CharFilter(lookup_type='icontains')

    class Meta:
        model = Network
        fields = ['network', 'name']


class NetworkList(generics.ListAPIView):
    queryset = Network.objects.all()
    serializer_class = NetworkSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('network', 'name',)
    filter_class = NetworkFilter
    paginate_by = 10


class AddressList(generics.ListAPIView):
    model = Address
    paginate_by = 50
    filter_backends = (filters.SearchFilter,)
    search_fields = ('address', 'mac',)


class DhcpGroupList(generics.ListAPIView):
    model = DhcpGroup
    filter_backends = (filters.SearchFilter,)
    filter_fields = ('name',)
