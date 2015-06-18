from django.contrib import admin
from django.apps import apps

app = apps.get_app_config('firewall')

for model_name, model in app.models.items():
    if 'Base' not in model_name and 'Log' not in model_name:
        admin.site.register(model)
