from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0016_ambulance_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='expertise_areas',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
