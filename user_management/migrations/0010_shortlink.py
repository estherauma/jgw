from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user_management", "0009_merge_0008_auto_20260330_0904_0008_auto_20260330_1125"),
    ]

    operations = [
        migrations.CreateModel(
            name="ShortLink",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=16, unique=True)),
                ("target_url", models.URLField(max_length=2048)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
