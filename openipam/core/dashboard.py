"""
This file was generated with the customdashboard management command, it
contains the two classes for the main dashboard and app index dashboard.
You can customize these classes as you want.

To activate your index dashboard add the following to your settings.py::
    ADMIN_TOOLS_INDEX_DASHBOARD = 'openipam.dashboard.CustomIndexDashboard'

And to activate the app index dashboard::
    ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'openipam.dashboard.CustomAppIndexDashboard'
"""

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from django.utils.text import capfirst
from django.contrib import admin
from django.db.models.aggregates import Count
from django.contrib.auth import get_user_model
from django.core.cache import cache

from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard
from admin_tools.utils import get_admin_site_name
from admin_tools.menu import items, Menu
from admin_tools.menu.items import MenuItem

from openipam.conf.ipam_settings import CONFIG
from openipam.hosts.models import Host
from openipam.core.modules import HTMLContentModule

from datetime import datetime

import qsstats

User = get_user_model()

class IPAMIndexDashboard(Dashboard):
    """
    Custom index dashboard for openipam.
    """

    title = ''

    def init_with_context(self, context):

        site_name = get_admin_site_name(context)
        request = context['request']

        #append an app list module for "IPAM"
        # self.children.append(modules.ModelList(
        #     _('Hosts'),
        #     models=(
        #         'openipam.hosts.*',
        #     ),
        # ))

        #self.children.append(modules.ModelList(
        #    _('Network'),
        #     models=(
        #         'openipam.network.*',
        #     ),
        # ))

        # self.children.append(modules.ModelList(
        #     _('Domains & DNS'),
        #     models=(
        #         'openipam.dns.*',
        #     ),
        # ))

        # append intro module
        self.children.append(HTMLContentModule(
            '<strong>Welcome to the new openIPAM interface.</strong>',
            html='''
                    <div style="margin: 10px 20px;">
                        <p><strong>Thank you for taking time to try out the new IPAM interface.</strong></p>
                        <p>
                            Since we are still in beta with this project, you may experience bugs.
                            We have provided a <a href="%(feature_request_link)s">feature and bug submission tool</a> to help aid us with features and bugs.
                            Please use this tool whenever possible as it will give us great feedback.
                        </p>
                        <p>Item to consider when using the new interface:</p>
                        <ul id="new-interface-list">
                            <li>Permissions - Do you have all your permissions?</li>
                            <li>Hosts - Do you see all your hosts?</li>
                            <li>DNS Entries - Do you see all DNS Entries?</li>
                            <li>Performance - Is the site slow?</li>
                        </ul>
                        <p>If you have any questions, please email:  <a href="%(email)s">%(email)s</a></p>
                    </div>
            ''' % {
                'email': CONFIG.get('EMAIL_ADDRESS'),
                'legacy_domain': CONFIG.get('LEGACY_DOMAIN'),
                'feature_request_link': reverse_lazy('feature_request')
            }
        ))

        if request.user.is_staff:
            # append an app list module for "Administration"
            self.children.append(modules.ModelList(
                _('Administration'),
                models=(
                    'openipam.user.models.User',
                    'rest_framework.authtoken.models.Token',
                    'django.contrib.*',
                    'guardian.*',
                    'openipam.core.*',
                    'openipam.log.models.EmailLog'
                ),
            ))

            # append crap to delete.
            self.children.append(modules.ModelList(
                _('TO BE DELETED'),
                models=(
                    'openipam.user.models.Permission',
                    'openipam.user.models.Group',
                    'openipam.user.models.UserToGroup',
                    'openipam.user.models.HostToGroup',
                    'openipam.user.models.DomainToGroup',
                    'openipam.user.models.NetworkToGroup',
                    'openipam.user.models.PoolToGroup',
                ),
            ))
        else:
            self.children.append(HTMLContentModule(
                'Navigation',
                html='''
                    <ul>
                        <li><a href="%(url_hosts)s">List Hosts</a></li>
                        <li><a href="%(url_add_hosts)s">Add Host</a></li>
                        <li><a href="%(url_dns)s">DNS Records</a></li>
                    </ul>
                    <ul>
                        <li style="border-top: 1px solid #e5e5e5;">
                            <a href="%(url_feature_request)s">Feature or Bug?</a>
                        </li>
                        <li><a href="%(url_profile)s">Profile</a></li>
                    </ul>
                ''' % {
                    'url_hosts': reverse_lazy('list_hosts'),
                    'url_add_hosts': reverse_lazy('add_hosts'),
                    'url_dns': reverse_lazy('list_dns'),
                    'url_feature_request': reverse_lazy('feature_request'),
                    'url_profile': reverse_lazy('profile'),
                }
            ))

        # append recent stats module
        hosts = Host.objects.all()
        hosts_stats = qsstats.QuerySetStats(hosts, 'changed', aggregate=Count('mac'), today=datetime.now())
        users = User.objects.all()
        users_stats = qsstats.QuerySetStats(users, 'date_joined', today=datetime.now())

        hosts_today = cache.get('hosts_today')
        hosts_week = cache.get('hosts_week')
        hosts_month = cache.get('hosts_month')

        if hosts_today is None:
            hosts_today = hosts_stats.this_day()
            cache.set('hosts_today', hosts_today)
        if hosts_week is None:
            hosts_week = hosts_stats.this_week()
            cache.set('hosts_week', hosts_week)
        if hosts_month is None:
            hosts_month = hosts_stats.this_month()
            cache.set('hosts_month', hosts_month)

        users_today = cache.get('users_today')
        users_week = cache.get('users_week')
        users_month = cache.get('users_month')

        if users_today is None:
            users_today = users_stats.this_day()
            cache.set('users_today', users_today)
        if users_week is None:
            users_week = users_stats.this_week()
            cache.set('users_week', users_week)
        if users_month is None:
            users_month = users_stats.this_month()
            cache.set('users_month', users_month)

        self.children.append(HTMLContentModule(
            'Recent Stats',
            html='''
                <div style="margin: 10px 20px;" class="well well-sm">
                    <h5>Hosts</h5>
                    <p><strong>%(hosts_today)s</strong> hosts changed today.</p>
                    <p><strong>%(hosts_week)s</strong> hosts changed this week.</p>
                    <p><strong>%(hosts_month)s</strong> hosts changed this month.</p>
                </div>
                <div style="margin: 10px 20px;" class="well well-sm">
                    <h5>Users</h5>
                    <p><strong>%(users_today)s</strong> users joined today.</p>
                    <p><strong>%(users_week)s</strong> users joined this week.</p>
                    <p><strong>%(users_month)s</strong> users joined this month.</p>
                </div>
            ''' % {
                'hosts_today': hosts_today,
                'hosts_week': hosts_week,
                'hosts_month': hosts_month,
                'users_today': users_today,
                'users_week': users_week,
                'users_month': users_month,
            }
        ))

        # append a recent actions module
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=5,

        ))


class IPAMAppList(modules.AppList):

    def init_with_context(self, context):
        super(IPAMAppList, self).init_with_context(context)


class IPAMAppIndexDashboard(AppIndexDashboard):
    """
    Custom app index dashboard for openipam.
    """

    # we disable title because its redundant with the model list module
    title = ''

    def __init__(self, *args, **kwargs):
        AppIndexDashboard.__init__(self, *args, **kwargs)

        #Hack for DNS App
        if 'dns' in self.app_title.lower():
            self.app_title = 'Domains & DNS'

        # append a model list module and a recent actions module
        self.children += [
            modules.ModelList(
                self.app_title,
                sorted(self.models)
            ),
            modules.RecentActions(
                _('Recent Actions'),
                include_list=self.get_app_content_types(),
                limit=5
            )
        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        return super(IPAMAppIndexDashboard, self).init_with_context(context)
