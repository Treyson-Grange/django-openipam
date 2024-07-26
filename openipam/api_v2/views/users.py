from rest_framework import generics
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from ..filters.users import UserFilterSet, AdvancedSearchFilter

from .base import APIPagination
from ..serializers.users import (
    RestrictedUserSerializer,
    UserSerializer,
    GroupSerializer,
)
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.contrib.auth.models import Group
from openipam.dns.models import Domain, DnsType
from openipam.hosts.models import Host
from openipam.network.models import Network, Pool

# Get the user model from Django
from django.contrib.auth import get_user_model

from guardian.shortcuts import assign_perm, remove_perm
from openipam.core.backends import IPAMLDAPBackend

import gc

User = get_user_model()

# from .base import APIModelViewSet, APIPagination


class UserView(generics.RetrieveAPIView):
    """API endpoint that allows users to be viewed."""

    permission_classes = [permissions.DjangoModelPermissions]
    # pagination_class = APIPagination
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get(self, pk=None):
        serializer = UserSerializer(self.request.user)
        if not pk and self.request.user.is_authenticated:
            return Response(serializer.data)
        return Response(serializer.data)


class GroupView(generics.ListAPIView):
    """API endpoint that allows groups to be viewed."""

    permission_classes = [permissions.DjangoModelPermissions]
    pagination_class = APIPagination
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["name"]

    def filter_queryset(self, queryset):
        name = self.request.query_params.get("name", None)
        order_by = self.request.query_params.get("order_by", None)
        direction = self.request.query_params.get("direction", None)

        if name is not None:
            queryset = queryset.filter(name__icontains=name)

        if order_by is not None and not "":
            if direction == "desc":
                order_by = f"-{order_by}"
            queryset = queryset.order_by(order_by)
        return queryset


class UserViewSet(viewsets.ModelViewSet):
    """Viewset for user objects. Does not allow user creation."""

    queryset = User.objects.prefetch_related("groups").all().order_by("-last_login")
    serializer_class = UserSerializer
    pagination_class = APIPagination
    permission_classes = [permissions.DjangoModelPermissions]
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        AdvancedSearchFilter,
    ]
    lookup_field = "username__iexact"
    filterset_class = UserFilterSet
    ordering_fields = ["username", "first_name", "last_name", "email", "is_active"]

    def get_serializer_class(self):
        """Use a restricted serializer for non-admin users."""
        if self.request.user.is_ipamadmin or self.action == "me":
            return self.serializer_class
        return RestrictedUserSerializer

    def get_queryset(self):
        """Only allow admins to list all users."""
        if not self.request.user.is_ipamadmin and self.action == "list":
            return self.queryset.filter(pk=self.request.user.pk)
        return self.queryset

    def create(self, request):
        """Create is not allowed, users are created via LDAP or shell."""
        return Response(status=405)

    def destroy(self, request, *args, **kwargs):
        """Destroy is not allowed, users are created via LDAP or shell."""
        return Response(status=405)

    def retrieve(self, request, username__iexact: str = None):
        """Return a single user by username."""
        username = username__iexact.lower()
        if username == self.request.user.username.lower():
            # Redirect to the "me" endpoint, which returns the current user with all fields
            # even if the user is not an admin.
            return Response(status=302, headers={"Location": self.reverse_action("me")})
        return super(UserViewSet, self).retrieve(request, username__iexact)

    @action(
        detail=False,
        methods=["get"],
        url_path=r"me",
        url_name="me",
    )
    def me(self, request):
        """Return the current user."""
        serializer = self.get_serializer(self.request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        url_path=r"me/groups",
        url_name="my-groups",
    )
    def my_groups(self, request):
        """Return the current users groups."""
        user = self.request.user
        return Response(user.groups.values_list("name", flat=True))

    def queryset_iterator(queryset, chunksize=1000):
        """''
        Iterate over a Django Queryset ordered by the primary key

        This method loads a maximum of chunksize (default: 1000) rows in it's
        memory at the same time while django normally would load all rows in it's
        memory. Using the iterator() method only causes it to not preload all the
        classes.

        Note that the implementation of the iterator does not support ordered query sets.
        """
        pk = 0
        last_pk = queryset.order_by("-pk")[0].pk
        queryset = queryset.order_by("pk")
        while pk < last_pk:
            for row in queryset.filter(pk__gt=pk)[:chunksize]:
                pk = row.pk
                yield row
            gc.collect()

    @action(
        detail=False,
        methods=["get"],
        url_path=r"ldap",
        url_name="ldap",
    )
    def populate_user_from_ldap(self, request):
        ldap_backend = IPAMLDAPBackend()
        users = request.query_params.get("users", None)
        if users is None:
            return Response(status=400, data={"detail": "Users are required."})

        for user in users:
            try:
                ldap_backend.populate_user(username=user)
            except Exception as e:
                return Response(status=500, data={"detail": f"Error: {e}"})
        return Response(status=201)

    @action(
        detail=False,
        methods=["post"],
        url_path=r"assign-object-permissions",
        url_name="assign-object-permissions",
    )
    def assign_object_permissions(self, request):
        """Assign object permssions to given users."""
        users = self.request.data.get("users", [])
        object = self.request.data.get("object", None)
        permission = self.request.data.get("permission", [])
        print(users, object, permission)
        if not users:
            return Response(status=400, data={"detail": "Users are required."})
        if not object:
            return Response(status=400, data={"detail": "Object is required."})
        if not permission:
            return Response(status=400, data={"detail": "Permission is required."})
        # assign object permission to users on object
        for user in users:
            try:
                user = User.objects.get(username=user)
                if "domain" in permission:
                    obj_instance = Domain.objects.get(name=object)
                elif "dnstype" in permission:
                    obj_instance = DnsType.objects.get(name=object)
                elif "host" in permission:
                    obj_instance = Host.objects.get(name=object)
                elif "network" in permission:
                    obj_instance = Network.objects.get(name=object)
                elif "pool" in permission:
                    obj_instance = Pool.objects.get(name=object)
                assign_perm(permission, user, obj_instance)
            except User.DoesNotExist:
                return Response(status=404, data={"detail": f"User {user} not found."})
            except Exception as e:
                return Response(status=500, data={"detail": f"Error: {e}"})
        return Response(status=201, data={"detail": "Permissions assigned."})

    @assign_object_permissions.mapping.delete
    def delete_object_permissions(self, request):
        """Delete object permssions to given users."""
        users = self.request.data.get("users", [])
        object = self.request.data.get("object", None)
        permission = self.request.data.get("permission", [])
        if not users:
            return Response(status=400, data={"detail": "Users are required."})
        if not object:
            return Response(status=400, data={"detail": "Object is required."})
        if not permission:
            return Response(status=400, data={"detail": "Permission is required."})
        # assign object permission to users on object
        for user in users:
            try:
                user = User.objects.get(username=user)
                if "domain" in permission:
                    obj_instance = Domain.objects.get(name=object)
                elif "dnstype" in permission:
                    obj_instance = DnsType.objects.get(name=object)
                elif "host" in permission:
                    obj_instance = Host.objects.get(name=object)
                elif "network" in permission:
                    obj_instance = Network.objects.get(name=object)
                elif "pool" in permission:
                    obj_instance = Pool.objects.get(name=object)
                remove_perm(permission, user, obj_instance)
            except User.DoesNotExist:
                return Response(status=404, data={"detail": f"User {user} not found."})
            except Exception as e:
                return Response(status=500, data={"detail": f"Error: {e}"})
        return Response(status=201, data={"detail": "Permissions removed."})

    @action(
        detail=False,
        methods=["get"],
        url_path=r"groups",
        url_name="groups",
        permission_classes=[permissions.IsAdminUser],
    )
    def groups(self, request):
        """Return the current user."""
        username = request.query_params.get("username", None)
        if username is None:
            return Response(status=400, data={"detail": "Username is required."})
        user = self.queryset.get(username=username)
        return Response(user.groups.values_list("name", flat=True))

    @groups.mapping.post
    def groups_post(self, request):
        """Add the given user to the given groups."""
        username = request.data.get("username", None)
        if username is None:
            return Response(status=400, data={"detail": "Username is required."})
        user = self.queryset.get(username=username)
        groups = request.data.get("groups", [])
        for group in groups:
            try:
                group = Group.objects.get(name=group)
                group.user_set.add(user)

            except Group.DoesNotExist:
                return Response(
                    status=404, data={"detail": f"Group {group} not found."}
                )
        return Response(user.groups.values_list("name", flat=True), status=201)

    @groups.mapping.delete
    def groups_delete(self, request):
        """Remove the user from the given groups."""
        username = request.data.get("username", None)
        if username is None:
            return Response(status=400, data={"detail": "Username is required."})
        user = self.queryset.get(username=username)
        groups = request.data.get("groups", [])
        for group in groups:
            try:
                Group.objects.get(name=group).user_set.remove(user)
            except Group.DoesNotExist:
                return Response(
                    status=404, data={"detail": f"Group {group} not found."}
                )
        return Response(user.groups.values_list("name", flat=True))
