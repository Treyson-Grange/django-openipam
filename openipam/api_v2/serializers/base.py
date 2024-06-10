"""Base serializers."""

from django.core.exceptions import ValidationError
from rest_framework import serializers
from netaddr import EUI, AddrFormatError, mac_bare
from openipam.user.models import User


class MACAddressField(serializers.CharField):
    """MAC Address field."""

    default_error_messages = {"invalid": "%(value)s is not a valid MAC address."}

    def validate(self, value):
        """Validate MAC address."""
        super(MACAddressField, self).validate(value)
        if value:
            try:
                value = EUI(str(value), dialect=mac_bare)
                return
            except (ValueError, TypeError, AddrFormatError, ValidationError):
                raise serializers.ValidationError(
                    self.error_messages["invalid"] % {"value": value}
                )


class IPAddressField(serializers.CharField):
    """IP Address field."""

    default_error_messages = {"invalid": "%(value)s is not a valid IP address."}

    def validate(self, value):
        """Validate IP address."""
        super(IPAddressField, self).validate(value)
        if value:
            try:
                return
            except (ValueError, TypeError, AddrFormatError, ValidationError):
                raise serializers.ValidationError(
                    self.error_messages["invalid"] % {"value": value}
                )


class ChangedBySerializer(serializers.ModelSerializer):
    """Serializer for the changed_by field."""

    def update(self, instance, validated_data):
        """Update changed_by field with context user."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    class Meta:
        """Meta class."""

        model = User
        fields = ("first_name", "last_name", "email", "username")
        extra_kwargs = {
            "username": {"validators": []},  # Avoid revalidating the username
        }
