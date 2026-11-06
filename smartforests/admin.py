from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from smartforests import models


@admin.register(models.CmsDocument, models.CmsImage)
class GenericAdmin(admin.ModelAdmin):
    pass


@admin.register(models.User)
class CustomUserAdmin(UserAdmin):
    pass


@admin.register(models.BlockedNetwork)
class BlockedNetworkAdmin(admin.ModelAdmin):
    list_display = (
        "network",
        "automatic",
        "ban_count",
        "expires_at",
        "reason",
        "updated_at",
    )
    list_filter = ("automatic",)
    search_fields = ("network", "reason")
    readonly_fields = ("created_at", "updated_at")
