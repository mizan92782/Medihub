from django.db import models
from django.conf import settings
from location.models import District, Division, Upozila
from core.enum import BloodGroupChoices, AvailabilityChoices, GenderChoices


class BloodDonor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blood_donor')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GenderChoices.choices)
    contact_number = models.CharField(max_length=15)
    profile_dp = models.ImageField(upload_to='donor/dp/', blank=True, null=True)

    blood_group = models.CharField(max_length=5, choices=BloodGroupChoices.choices)
    availability = models.CharField(max_length=15, choices=AvailabilityChoices.choices, default=AvailabilityChoices.AVAILABLE)
    last_donated = models.DateField(blank=True, null=True)
    lives_saved_count = models.PositiveIntegerField(default=0)

    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    upozila = models.ForeignKey(Upozila, on_delete=models.SET_NULL, null=True)

    address = models.TextField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.blood_group}'


class BloodDonationPost(models.Model):
    donor = models.ForeignKey(BloodDonor, on_delete=models.CASCADE, related_name='donation_posts')
    patient_description = models.TextField()
    medical_facility = models.CharField(max_length=300)
    donation_date = models.DateField()
    donation_time = models.TimeField()
    bags_donated = models.PositiveSmallIntegerField(default=1)
    
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    upozila = models.ForeignKey(Upozila, on_delete=models.SET_NULL, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'Donation by {self.donor} on {self.donation_date}'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.donor:
            # Auto-increment life counter in donor profile to encourage donors
            BloodDonor.objects.filter(pk=self.donor_id).update(
                lives_saved_count=models.F('lives_saved_count') + 1,
                last_donated=self.donation_date
            )
