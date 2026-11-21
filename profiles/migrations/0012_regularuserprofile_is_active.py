from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0011_blooddonor_add_is_available'),
    ]

    operations = [
        migrations.AddField(
            model_name='regularuserprofile',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
