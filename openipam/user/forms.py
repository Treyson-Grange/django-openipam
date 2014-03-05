from django import forms
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.conf import settings
from django.db.models import Q

from openipam.user.models import User

from guardian.models import UserObjectPermission, GroupObjectPermission

import autocomplete_light

import operator


class AuthUserCreateAdminForm(UserCreationForm):
    def clean_username(self):
        username = self.cleaned_data['username'].lower()

        if User.objects.filter(username=username):
            raise forms.ValidationError('Username already exists.')

        return super(self, AuthUserCreateAdminForm).clean_username()


    class Meta:
        model = User


class AuthUserChangeAdminForm(UserChangeForm):

    def clean_username(self):
        #assert False, self.instance.username
        username = self.cleaned_data['username']
        db_user = User.objects.filter(username__iexact=username)

        if 'username' in self.changed_data and db_user and db_user[0] != self.instance:
            raise forms.ValidationError('Username already exists.')

        return username

    class Meta:
        model = User


class AuthGroupAdminForm(forms.ModelForm):

    def clean_name(self):
        name = self.cleaned_data['name'].lower()

        if Group.objects.filter(name=name):
            raise forms.ValidationError('Group name already exists.')

        return name

    class Meta:
        model = Group


PERMISSION_FILTER = [
    Q(codename__startswith='add_records_to'),
    Q(codename__startswith='is_owner'),
]


class UserObjectPermissionAdminForm(forms.ModelForm):
    user = forms.ModelChoiceField(User.objects.all(), widget=autocomplete_light.ChoiceWidget('UserAutocomplete'))
    permission = forms.ModelChoiceField(Permission.objects.filter(reduce(operator.or_, PERMISSION_FILTER)), label='Permission')
    # permission = forms.ModelChoiceField(Permission.objects.filter(content_type__app_label__in=settings.IPAM_APPS),
    #     widget=autocomplete_light.ChoiceWidget('PermissionAutocomplete'), label='Permission')
    object_id = forms.CharField(widget=autocomplete_light.ChoiceWidget('IPAMObjectsAutoComplete'), label='Object')

    # def __init__(self, *args, **kwargs):
    #     super(UserObjectPermissionAdminForm, self).__init__(*args, **kwargs)

    #     if self.instance:
    #        self.fields['object_id'].initial = '%s-%s' % (self.instance.content_type.pk, self.instance.object_pk)

    class Meta:
        model = UserObjectPermission
        exclude = ('content_type', 'object_pk',)


class GroupObjectPermissionAdminForm(forms.ModelForm):
    group = forms.ModelChoiceField(Group.objects.all(), widget=autocomplete_light.ChoiceWidget('GroupAutocomplete'))
    permission = forms.ModelChoiceField(Permission.objects.filter(reduce(operator.or_, PERMISSION_FILTER)), label='Permission')
    object_id = forms.CharField(widget=autocomplete_light.ChoiceWidget('IPAMObjectsAutoComplete'), label='Object')

    # def __init__(self, *args, **kwargs):
    #     super(UserObjectPermissionAdminForm, self).__init__(*args, **kwargs)

    #     if self.instance:
    #        self.fields['object_id'].initial = '%s-%s' % (self.instance.content_type.pk, self.instance.object_pk)

    class Meta:
        model = GroupObjectPermission
        exclude = ('content_type', 'object_pk')
