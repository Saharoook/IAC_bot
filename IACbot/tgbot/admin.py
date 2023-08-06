from django.contrib import admin
from .models import TgUser, Organization


admin.site.register(TgUser)
admin.site.register(Organization)
