from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("user_management", "0004_alter_appuser_work_groups"),
    ]

    operations = [
        migrations.DeleteModel(
            name="AppUser",
        ),
    ]
