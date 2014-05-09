from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
from django import forms

from openipam.network.models import AddressType, DhcpOptionToDhcpGroup, DhcpGroup

import autocomplete_light

from curses.ascii import isprint

import binascii


class AddressTypeAdminForm(forms.ModelForm):

    def clean(self):
        ranges = self.cleaned_data.get('ranges', [])
        pool = self.cleaned_data.get('pool', '')

        if pool and ranges:
            raise ValidationError(_('Address Types cannot have both a pool and a range.'))

        return self.cleaned_data

    class Meta:
        model = AddressType


class DhcpOptionToDhcpGroupAdminForm(forms.ModelForm):
    group = forms.ModelChoiceField(DhcpGroup.objects.all(),
        widget=autocomplete_light.ChoiceWidget('DhcpGroupAutocomplete')
    )
    readable_value = forms.CharField(label='Value')

    def __init__(self, *args, **kwargs):
        super(DhcpOptionToDhcpGroupAdminForm, self).__init__(*args, **kwargs)

        if self.instance:
            printable = True
            for c in self.instance.value:
                if not isprint(c):
                    printable = False
                    break

            if printable:
                self.fields['readable_value'].initial = self.instance.value
            else:
                self.fields['readable_value'].initial = '0x' + binascii.hexlify(self.instance.value)

            self.original_value = self.fields['readable_value'].initial


    def clean_readable_value(self):
        value = self.cleaned_data['readable_value']
        if value[:2] == '0x':
            self.instance.value = binascii.unhexlify(value[2:])
        else:
            self.instance.value = str(value)

        return value


    class Meta:
        model = DhcpOptionToDhcpGroup

