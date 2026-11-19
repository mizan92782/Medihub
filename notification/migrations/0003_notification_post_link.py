from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0002_device_user_alter_device_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='appnotification',
            name='post_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='appnotification',
            name='post_type',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
