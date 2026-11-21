from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0001_initial'),
        ('post', '0005_alter_ambulanceneedpost_ambulance_type'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EquipmentSellPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('equipment_name', models.CharField(max_length=300)),
                ('quantity', models.CharField(max_length=100)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('condition', models.CharField(choices=[('new', 'New'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor')], default='good', max_length=10)),
                ('description', models.TextField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('contact_number', models.CharField(max_length=15)),
                ('status', models.CharField(choices=[('open', 'Open'), ('fulfilled', 'Fulfilled'), ('closed', 'Closed')], default='open', max_length=15)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('district', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.district')),
                ('division', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.division')),
                ('upozila', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.upozila')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='equipment_sell_posts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='MedicinePost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('listing_type', models.CharField(choices=[('buy', 'Want to Buy'), ('sell', 'Want to Sell')], default='buy', max_length=10)),
                ('medicine_name', models.CharField(max_length=300)),
                ('quantity', models.CharField(max_length=100)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('contact_number', models.CharField(max_length=15)),
                ('status', models.CharField(choices=[('open', 'Open'), ('fulfilled', 'Fulfilled'), ('closed', 'Closed')], default='open', max_length=15)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('district', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.district')),
                ('division', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.division')),
                ('upozila', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.upozila')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medicine_posts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
    ]
