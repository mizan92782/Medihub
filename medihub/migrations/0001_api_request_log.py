from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authentication', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='APIRequestLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=500)),
                ('method', models.CharField(max_length=10)),
                ('status_code', models.IntegerField(default=200)),
                ('ip', models.GenericIPAddressField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='authentication.user')),
            ],
            options={
                'indexes': [models.Index(fields=['created'], name='medihub_api_created_idx')],
            },
        ),
    ]
