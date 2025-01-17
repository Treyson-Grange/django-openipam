# Generated by Django 2.2.4 on 2019-08-09 22:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import djorm_pgfulltext.fields
import netfields.fields
import taggit.managers


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("hosts", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("taggit", "0002_auto_20150616_2121"),
    ]

    operations = [
        migrations.CreateModel(
            name="Building",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(blank=True, max_length=255)),
                ("number", models.CharField(max_length=255, unique=True)),
                (
                    "abbreviation",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("city", models.CharField(blank=True, max_length=255)),
                ("description", models.TextField()),
                ("changed", models.DateTimeField(auto_now=True)),
                (
                    "changed_by",
                    models.ForeignKey(
                        db_column="changed_by",
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "buildings"},
        ),
        migrations.CreateModel(
            name="BuildingToVlan",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("tagged", models.BooleanField(default=False)),
                ("changed", models.DateTimeField(auto_now=True)),
                (
                    "building",
                    models.ForeignKey(
                        db_column="building",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="network.Building",
                    ),
                ),
                (
                    "changed_by",
                    models.ForeignKey(
                        db_column="changed_by",
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "buildings_to_vlans"},
        ),
        migrations.CreateModel(
            name="DhcpGroup",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.SlugField()),
                ("description", models.TextField(blank=True, null=True)),
                ("changed", models.DateTimeField(auto_now=True)),
                (
                    "changed_by",
                    models.ForeignKey(
                        db_column="changed_by",
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"verbose_name": "DHCP group", "db_table": "dhcp_groups"},
        ),
        migrations.CreateModel(
            name="DhcpOption",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("size", models.CharField(blank=True, max_length=10, null=True)),
                (
                    "name",
                    models.CharField(
                        blank=True, max_length=255, null=True, unique=True
                    ),
                ),
                (
                    "option",
                    models.CharField(
                        blank=True, max_length=255, null=True, unique=True
                    ),
                ),
                ("comment", models.TextField(blank=True, null=True)),
            ],
            options={"verbose_name": "DHCP option", "db_table": "dhcp_options"},
        ),
        migrations.CreateModel(
            name="Network",
            fields=[
                (
                    "network",
                    netfields.fields.CidrAddressField(
                        max_length=43, primary_key=True, serialize=False
                    ),
                ),
                ("name", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "gateway",
                    netfields.fields.InetAddressField(
                        blank=True, max_length=39, null=True
                    ),
                ),
                ("description", models.TextField(blank=True, null=True)),
                ("changed", models.DateTimeField(auto_now=True)),
                (
                    "search_index",
                    djorm_pgfulltext.fields.VectorField(
                        db_index=True,
                        default="",
                        editable=False,
                        null=True,
                        serialize=False,
                    ),
                ),
                (
                    "changed_by",
                    models.ForeignKey(
                        db_column="changed_by",
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "dhcp_group",
                    models.ForeignKey(
                        blank=True,
                        db_column="dhcp_group",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="network.DhcpGroup",
                    ),
                ),
            ],
            options={
                "db_table": "networks",
                "ordering": ("network",),
                "permissions": (
                    ("is_owner_network", "Is owner"),
                    ("add_records_to_network", "Can add records to"),
                ),
                "default_permissions": ("add", "change", "delete", "view"),
            },
        ),
        migrations.CreateModel(
            name="NetworkRange",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "range",
                    netfields.fields.CidrAddressField(max_length=43, unique=True),
                ),
            ],
            options={"db_table": "network_ranges"},
        ),
        migrations.CreateModel(
            name="Vlan",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("vlan_id", models.SmallIntegerField()),
                ("name", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                ("changed", models.DateTimeField(auto_now=True)),
                (
                    "buildings",
                    models.ManyToManyField(
                        related_name="building_vlans",
                        through="network.BuildingToVlan",
                        to="network.Building",
                    ),
                ),
                (
                    "changed_by",
                    models.ForeignKey(
                        db_column="changed_by",
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "vlans"},
        ),
        migrations.CreateModel(
            name="TaggedNetworks",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "content_object",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="network.Network",
                    ),
                ),
                (
                    "tag",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="network_taggednetworks_items",
                        to="taggit.Tag",
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="SharedNetwork",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("changed", models.DateTimeField(auto_now=True)),
                (
                    "changed_by",
                    models.ForeignKey(
                        db_column="changed_by",
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "shared_networks"},
        ),
        migrations.CreateModel(
            name="Pool",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.SlugField()),
                ("description", models.TextField(blank=True)),
                ("allow_unknown", models.BooleanField(default=False)),
                ("lease_time", models.IntegerField()),
                ("assignable", models.BooleanField(default=False)),
                (
                    "dhcp_group",
                    models.ForeignKey(
                        blank=True,
                        db_column="dhcp_group",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="network.DhcpGroup",
                    ),
                ),
            ],
            options={
                "db_table": "pools",
                "permissions": (("add_records_to_pool", "Can add records to"),),
            },
        ),
        migrations.AddField(
            model_name="network",
            name="shared_network",
            field=models.ForeignKey(
                blank=True,
                db_column="shared_network",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="network.SharedNetwork",
            ),
        ),
        migrations.AddField(
            model_name="network",
            name="tags",
            field=taggit.managers.TaggableManager(
                blank=True,
                help_text="A comma-separated list of tags.",
                through="network.TaggedNetworks",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        ),
        migrations.CreateModel(
            name="HostToPool",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("changed", models.DateTimeField(auto_now=True)),
                (
                    "changed_by",
                    models.ForeignKey(
                        db_column="changed_by",
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "host",
                    models.ForeignKey(
                        db_column="mac",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="host_pools",
                        to="hosts.Host",
                    ),
                ),
                (
                    "pool",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="host_pools",
                        to="network.Pool",
                    ),
                ),
            ],
            options={"db_table": "hosts_to_pools"},
        ),
        migrations.CreateModel(
            name="DhcpOptionToDhcpGroup",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("value", models.BinaryField(blank=True, null=True)),
                ("changed", models.DateTimeField(auto_now=True)),
                (
                    "changed_by",
                    models.ForeignKey(
                        db_column="changed_by",
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        blank=True,
                        db_column="gid",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="option_values",
                        to="network.DhcpGroup",
                    ),
                ),
                (
                    "option",
                    models.ForeignKey(
                        blank=True,
                        db_column="oid",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="group_values",
                        to="network.DhcpOption",
                    ),
                ),
            ],
            options={"db_table": "dhcp_options_to_dhcp_groups"},
        ),
        migrations.AddField(
            model_name="dhcpgroup",
            name="dhcp_options",
            field=models.ManyToManyField(
                through="network.DhcpOptionToDhcpGroup", to="network.DhcpOption"
            ),
        ),
        migrations.CreateModel(
            name="DefaultPool",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("cidr", netfields.fields.CidrAddressField(max_length=43, unique=True)),
                (
                    "pool",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="pool_defaults",
                        to="network.Pool",
                    ),
                ),
            ],
            options={"db_table": "default_pools"},
        ),
        migrations.AddField(
            model_name="buildingtovlan",
            name="vlan",
            field=models.ForeignKey(
                db_column="vlan",
                on_delete=django.db.models.deletion.CASCADE,
                to="network.Vlan",
            ),
        ),
        migrations.CreateModel(
            name="AddressType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("is_default", models.BooleanField(default=False)),
                (
                    "pool",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="network.Pool",
                    ),
                ),
                (
                    "ranges",
                    models.ManyToManyField(
                        blank=True,
                        related_name="address_ranges",
                        to="network.NetworkRange",
                    ),
                ),
            ],
            options={"db_table": "addresstypes", "ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="Address",
            fields=[
                (
                    "address",
                    netfields.fields.InetAddressField(
                        max_length=39, primary_key=True, serialize=False
                    ),
                ),
                ("reserved", models.BooleanField(default=False)),
                ("changed", models.DateTimeField(auto_now=True)),
                (
                    "changed_by",
                    models.ForeignKey(
                        db_column="changed_by",
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "host",
                    models.ForeignKey(
                        blank=True,
                        db_column="mac",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="addresses",
                        to="hosts.Host",
                    ),
                ),
                (
                    "network",
                    models.ForeignKey(
                        db_column="network",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="net_addresses",
                        to="network.Network",
                    ),
                ),
                (
                    "pool",
                    models.ForeignKey(
                        blank=True,
                        db_column="pool",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="network.Pool",
                    ),
                ),
            ],
            options={"verbose_name_plural": "addresses", "db_table": "addresses"},
        ),
        migrations.CreateModel(
            name="NetworkToVlan",
            fields=[
                (
                    "network",
                    models.OneToOneField(
                        db_column="network",
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to="network.Network",
                    ),
                ),
                ("changed", models.DateTimeField(auto_now=True)),
                (
                    "changed_by",
                    models.ForeignKey(
                        db_column="changed_by",
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "vlan",
                    models.ForeignKey(
                        db_column="vlan",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="network.Vlan",
                    ),
                ),
            ],
            options={"db_table": "networks_to_vlans"},
        ),
        migrations.AddField(
            model_name="network",
            name="vlans",
            field=models.ManyToManyField(
                related_name="vlan_networks",
                through="network.NetworkToVlan",
                to="network.Vlan",
            ),
        ),
        migrations.CreateModel(
            name="Lease",
            fields=[
                (
                    "address",
                    models.OneToOneField(
                        db_column="address",
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="leases",
                        serialize=False,
                        to="network.Address",
                    ),
                ),
                ("abandoned", models.BooleanField(default=False)),
                ("server", models.CharField(blank=True, max_length=255, null=True)),
                ("starts", models.DateTimeField()),
                ("ends", models.DateTimeField()),
                (
                    "host",
                    models.ForeignKey(
                        db_column="mac",
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="leases",
                        to="hosts.Host",
                    ),
                ),
            ],
            options={"db_table": "leases"},
        ),
        migrations.AlterUniqueTogether(
            name="buildingtovlan", unique_together={("building", "vlan")}
        ),
    ]
