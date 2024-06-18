"""Serializers for network objects."""

from openipam.api_v2.serializers.base import ChangedBySerializer
from openipam.network.models import (
    Address,
    Building,
    BuildingToVlan,
    DhcpGroup,
    DhcpOption,
    DhcpOptionToDhcpGroup,
    Vlan,
    Network,
    Pool,
    DefaultPool,
    AddressType,
    SharedNetwork,
    NetworkRange,
    NetworkToVlan,
    Lease,
)
from rest_framework import serializers as base_serializers
from rest_framework.serializers import (
    ModelSerializer,
    Field,
    SerializerMethodField,
    CharField,
)
from netfields.rest_framework import CidrAddressField
from django.shortcuts import get_object_or_404
import ipaddress


class VlanBuildingSerializer(ModelSerializer):
    class Meta:
        model = Building
        fields = ["id", "number", "abbreviation", "name"]


class VlanNetworkSerializer(ModelSerializer):
    class Meta:
        model = Network
        fields = ["network", "name", "gateway", "dhcp_group", "shared_network"]


class VlanSerializer(ModelSerializer):
    """Serializer for vlan objects."""

    buildings = VlanBuildingSerializer(many=True, read_only=True)
    vlan_networks = VlanNetworkSerializer(many=True, read_only=True)

    class Meta:
        """Meta class for vlan serializer."""

        model = Vlan
        fields = "__all__"


class SharedNetworkSerializer(ModelSerializer):
    """Serializer for shared network objects."""

    changed_by = SerializerMethodField()

    def get_changed_by(self, obj):
        return obj.changed_by.username if obj.changed_by else None

    def perform_create(self, serializer):
        serializer.save(changed_by=self.context["request"].user)

    class Meta:
        """Meta class for shared network serializer."""

        model = SharedNetwork
        fields = ["id", "name", "description", "changed", "changed_by"]


class NetworkRangeSerializer(ModelSerializer):
    """Serializer for network range objects."""

    class Meta:
        """Meta class for network range serializer."""

        model = NetworkRange
        fields = "__all__"

    def create(self, validated_data):
        """Override create method to handle NetworkRange creation."""
        range = validated_data.pop("range")
        network_range = NetworkRange.objects.create(range=range)
        return network_range


class NetworkToVlanSerializer(ChangedBySerializer):
    network = CidrAddressField()

    def validate_network(self, value):
        if value:
            network_exists = Network.objects.filter(network=value).first()
            if not network_exists:
                raise serializers.ValidationError("The network entered does not exist.")
            return network_exists
        return None

    class Meta:
        model = NetworkToVlan
        fields = "__all__"


class NetworkSerializer(ModelSerializer):
    """Serializer for network objects."""

    vlans = VlanSerializer(many=True)
    buildings = SerializerMethodField()
    shared_network = SerializerMethodField()
    gateway = base_serializers.CharField(source="gateway.ip", read_only=True)
    addresses = SerializerMethodField()
    changed_by = SerializerMethodField()
    dhcp_group = base_serializers.SlugRelatedField(slug_field="name", read_only=True)

    def get_changed_by(self, obj):
        return obj.changed_by.username if obj.changed_by else None

    def get_addresses(self, obj):
        """Return a link to the address listing"""
        return self.context["request"].build_absolute_uri(
            f"/api/v2/networks/{obj.pk}/addresses/"
        )

    def get_shared_network(self, obj):
        if obj.shared_network:
            return {
                "id": obj.shared_network.id,
                "name": obj.shared_network.name,
                "description": obj.shared_network.description,
            }
        else:
            return None

    def get_buildings(self, obj):
        # Buildings are linked to vlans, so we need to get the vlans for the network
        # and then get the buildings for those vlans
        buildings = Building.objects.none()
        for vlan in obj.vlans.all():
            buildings |= vlan.buildings.all()
        return buildings.distinct().values(
            "id", "name", "abbreviation", "number", "city"
        )

    def create(self, validated_data):
        changed_by_data = validated_data.pop("changed_by", None)
        if changed_by_data:
            changed_by_instance = self.context["request"].user
            validated_data["changed_by"] = changed_by_instance
        return super().create(validated_data)

    class Meta:
        """Meta class for network serializer."""

        model = Network
        fields = "__all__"


class SimpleNetworkSerializer(Field):
    """Network serializer that functions on CIDR format only."""

    def to_representation(self, value):
        """Convert network object to CIDR format."""
        return str(value.network)

    def to_internal_value(self, data):
        """Find network object based on CIDR."""
        network = get_object_or_404(Network, network=data)
        return network


class DhcpGroupSerializer(ModelSerializer):
    """Serializer for DHCP group objects."""

    changed_by = SerializerMethodField()

    class Meta:
        model = DhcpGroup
        fields = "__all__"

    def update(self, instance, validated_data):
        changed_by_data = validated_data.pop("changed_by", None)
        if changed_by_data:
            changed_by_serializer = self.fields["changed_by"]
            changed_by_instance = instance.changed_by
            changed_by_serializer.update(changed_by_instance, changed_by_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def create(self, validated_data):
        changed_by_data = validated_data.pop("changed_by", None)
        if changed_by_data:
            changed_by_instance = self.context["request"].user
            validated_data["changed_by"] = changed_by_instance
        return super().create(validated_data)

    def get_changed_by(self, obj):
        return obj.changed_by.username if obj.changed_by else None


from rest_framework import serializers


class DhcpOptionSerializer(serializers.ModelSerializer):
    """Serializer for dhcp option objects."""

    class Meta:
        """Meta class for dhcp option serializer."""

        model = DhcpOption
        fields = "__all__"


class BinaryDataField(serializers.Field):
    def to_representation(self, obj):
        return obj.hex()

    def to_internal_value(self, data):
        return bytes.fromhex(data)


class DhcpOptionToDhcpGroupSerializer(serializers.ModelSerializer):
    """Serializer for dhcp option to dhcp group objects."""

    changed_by = serializers.SlugRelatedField(slug_field="username", read_only=True)
    option = serializers.SlugRelatedField(
        slug_field="name", queryset=DhcpOption.objects.all()
    )
    group = serializers.SlugRelatedField(
        slug_field="name", queryset=DhcpGroup.objects.all()
    )
    value = BinaryDataField()
    readable_value = serializers.CharField(
        source="get_readable_value", read_only=True, label="value"
    )

    def create(self, validated_data):
        changed_by = self.context["request"].user
        validated_data["changed_by"] = changed_by
        return super().create(validated_data)

    class Meta:
        model = DhcpOptionToDhcpGroup
        fields = (
            "id",
            "option",
            "group",
            "value",
            "changed_by",
            "changed",
            "readable_value",
        )


class DhcpOptionToDhcpGroupDeleteSerializer(ModelSerializer):
    """Serializer for deleting dhcp options from a dhcp group."""

    class Meta:
        """Meta class for dhcp option to dhcp group delete serializer."""

        model = DhcpOptionToDhcpGroup
        fields = ("group", "option", "value")
        read_only_fields = ("group", "option", "value")


class SimpleDhcpGroupSerializer(Field):
    """Dhcp Group serializer that functions on name format only."""

    def to_representation(self, value):
        """Convert dhcp group object to name format."""
        return str(value.name)

    def to_internal_value(self, data):
        """Find dhcp group object based on name."""
        dhcp_group = get_object_or_404(DhcpGroup, name=data)
        return dhcp_group


class PoolSerializer(ModelSerializer):
    """Address pool serializer."""

    dhcp_group = SimpleDhcpGroupSerializer()

    class Meta:
        """Meta class for pool serializer."""

        model = Pool
        fields = "__all__"


class DefaultPoolSerializer(ModelSerializer):
    """Default pool serializer."""

    pool_name = base_serializers.CharField(
        source="pool.name", read_only=True, default=""
    )

    class Meta:
        """Meta class for default"""

        model = DefaultPool
        fields = "__all__"


class SimpleAddressSerializer(Field):
    """Address serializer that functions string representation only."""

    def to_representation(self, value):
        """Convert address object to string."""
        return str(value)

    def to_internal_value(self, data):
        """Find address object based on string."""
        address = get_object_or_404(Address, address=data)
        return address


class AddressSerializer(ModelSerializer):
    """Serializer for address objects."""

    network = SimpleNetworkSerializer()
    gateway = base_serializers.CharField(source="network.gateway.ip", read_only=True)
    pool = PoolSerializer()
    address = SimpleAddressSerializer()
    hostname = base_serializers.CharField(source="host.hostname", read_only=True)
    host = base_serializers.CharField(source="host_id", read_only=True)

    def validate_network(self, value):
        """Validate that the network contains the address."""
        # get an ip address object from the address field
        address = self.initial_data.get("address")
        if not address:
            raise base_serializers.ValidationError("Address is required.")
        try:
            address = ipaddress.ip_address(address)
        except ValueError:
            raise base_serializers.ValidationError("Invalid IP address.")
        if address not in value.network:
            raise base_serializers.ValidationError("Address is not in network.")
        return value

    class Meta:
        """Meta class for address serializer."""

        model = Address
        fields = (
            "address",
            "pool",
            "reserved",
            "network",
            "changed",
            "gateway",
            "host",
            "hostname",
            "last_seen",
            "last_mac_seen",
        )


class AddressCidrField(Field):
    def to_representation(self, value):
        """Convert address object to string."""
        return str(value)

    def to_internal_value(self, data):
        """Find address object based on string."""
        return ipaddress.ip_interface(data)


class AddressTypeSerializer(ModelSerializer):
    ranges = base_serializers.StringRelatedField(read_only=True, many=True)
    pool = base_serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = AddressType
        fields = "__all__"


class LeaseSerializer(ModelSerializer):
    """Serializer for lease objects."""

    address = CharField(read_only=False)
    host = serializers.CharField(allow_null=True)

    starts = base_serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    ends = base_serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    def update(self, instance, validated_data):
        address_data = validated_data.pop("address", None)
        if address_data:
            try:
                address_instance = Address.objects.get(address=address_data)
                validated_data["address"] = address_instance
            except Address.DoesNotExist:
                raise serializers.ValidationError(
                    f"Address {address_data} does not exist"
                )

        return super().update(instance, validated_data)

    class Meta:
        """Meta class for lease serializer."""

        model = Lease
        fields = "__all__"


class BuildingVlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vlan
        fields = ["id", "vlan_id", "name", "description"]


class BuildingSerializer(ModelSerializer):
    """Serializer for building objects."""

    building_vlans = BuildingVlanSerializer(many=True, read_only=True)

    def create(self, validated_data):
        changed_by_data = validated_data.pop("changed_by", None)
        if changed_by_data:
            changed_by_instance = self.context["request"].user
            validated_data["changed_by"] = changed_by_instance
        return super().create(validated_data)

    class Meta:
        """Meta class for building serializer."""

        model = Building
        fields = "__all__"
        read_only_fields = ("building_vlans",)


class BuildingToVlanSerializer(ModelSerializer):
    """Serializer for building to vlan objects."""

    building_name = SerializerMethodField()

    def get_building_name(self, obj):
        return obj.building.name

    class Meta:
        """Meta class for building to vlan serializer."""

        model = BuildingToVlan
        fields = "__all__"
