from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from smartforests import models


@admin.register(models.CmsDocument, models.CmsImage)
class GenericAdmin(admin.ModelAdmin):
    pass


@admin.register(models.User)
class CustomUserAdmin(UserAdmin):
    pass
