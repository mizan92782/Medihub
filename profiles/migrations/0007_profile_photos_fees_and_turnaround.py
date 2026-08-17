from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0006_doctorscheduling_hospital_and_more"),
    ]

    operations = [
        # Fields the frontend already reads but that had no column behind them.
        migrations.AddField(
            model_name="doctor",
            name="consultation_fee",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name="doctor",
            name="address",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="diagnostictest",
            name="turnaround_time",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        # Profile photos for the remaining profile types.
        migrations.AddField(
            model_name="blooddonor",
            name="profile_dp",
            field=models.ImageField(blank=True, null=True, upload_to="donor/dp/"),
        ),
        migrations.AddField(
            model_name="ambulanceprofile",
            name="profile_dp",
            field=models.ImageField(blank=True, null=True, upload_to="ambulance/dp/"),
        ),
        migrations.AddField(
            model_name="pharmacyprofile",
            name="profile_dp",
            field=models.ImageField(blank=True, null=True, upload_to="pharmacy/dp/"),
        ),
        migrations.AddField(
            model_name="diagnosticprofile",
            name="profile_dp",
            field=models.ImageField(blank=True, null=True, upload_to="diagnostic/dp/"),
        ),
    ]
