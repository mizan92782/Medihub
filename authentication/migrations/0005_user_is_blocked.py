from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_user_two_factor_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_blocked',
            field=models.BooleanField(default=False),
        ),
    ]
