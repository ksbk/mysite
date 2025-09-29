from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SiteSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("site_name", models.CharField(default="MySite", max_length=200)),
                ("meta_description", models.CharField(blank=True, default="", max_length=300)),
                ("meta_keywords", models.CharField(blank=True, default="", max_length=300)),
                ("og_image", models.URLField(blank=True, default="")),
            ],
            options={
                "verbose_name": "Site settings",
            },
        ),
    ]
