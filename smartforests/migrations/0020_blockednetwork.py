from datetime import timedelta

from django.db import migrations, models
from django.utils import timezone

# Ranges used by the 6 Nov 2026 scraper flood, previously hard-coded in
# smartforests/middleware.py. Seeded with a 7-day expiry; after that the rate
# limiter re-bans them automatically if they come back.
SEED_NETWORKS = ["145.223.0.0/16", "84.75.0.0/16", "82.38.0.0/16"]


def seed(apps, schema_editor):
    BlockedNetwork = apps.get_model("smartforests", "BlockedNetwork")
    expires_at = timezone.now() + timedelta(days=7)
    for network in SEED_NETWORKS:
        BlockedNetwork.objects.get_or_create(
            network=network,
            defaults={
                "reason": "Scraper flood, 6 Nov 2026",
                "automatic": False,
                "expires_at": expires_at,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ("smartforests", "0019_alter_cmsimage_file"),
    ]

    operations = [
        migrations.CreateModel(
            name="BlockedNetwork",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("network", models.CharField(help_text="An IP address or CIDR range, e.g. 203.0.113.0/24", max_length=64, unique=True)),
                ("reason", models.CharField(blank=True, max_length=255)),
                ("automatic", models.BooleanField(default=False, help_text="Created by the rate limiter rather than by hand")),
                ("ban_count", models.PositiveIntegerField(default=1, help_text="Times this network has been banned")),
                ("expires_at", models.DateTimeField(blank=True, help_text="Leave empty to block permanently", null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["-updated_at"]},
        ),
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
