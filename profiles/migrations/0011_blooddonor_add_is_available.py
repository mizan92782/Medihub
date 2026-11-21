from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0010_ambulanceprofile_cover_photo_blooddonor_cover_photo_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='blooddonor',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
    ]
