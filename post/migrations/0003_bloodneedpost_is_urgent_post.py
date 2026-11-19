from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0002_postshare_postcomment_ambulanceneedpost_postlike'),
    ]

    operations = [
        migrations.AddField(
            model_name='bloodneedpost',
            name='is_urgent_post',
            field=models.BooleanField(default=False),
        ),
    ]
