import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0015_alter_ambulanceprofile_ambulance_type'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AmbulanceReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('opinion', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('ambulance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='profiles.ambulanceprofile')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ambulance_reviews', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
                'unique_together': {('ambulance', 'user')},
            },
        ),
    ]
