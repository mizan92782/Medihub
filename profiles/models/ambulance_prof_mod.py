from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from location.models import District, Division, Upozila

from core.enum import AmbulanceTypeChoices


class AmbulanceProfile(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ambulance')
    owner_name = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=15)
    ambulance_type = models.CharField(max_length=20, choices=AmbulanceTypeChoices.choices)
    vehicle_number = models.CharField(max_length=50, unique=True)
    is_available = models.BooleanField(default=True)   # user-controlled: ambulance ready for dispatch
    is_active = models.BooleanField(default=True)      # user-controlled: hides profile from public
    profile_dp = models.ImageField(upload_to='ambulance/dp/', blank=True, null=True)
    cover_photo = models.ImageField(upload_to='ambulance/cover/', blank=True, null=True)

    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    upozila = models.ForeignKey(Upozila, on_delete=models.SET_NULL, null=True)
    address = models.TextField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.owner_name} - {self.vehicle_number}'


class AmbulanceReview(models.Model):
    ambulance = models.ForeignKey(AmbulanceProfile, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ambulance_reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    opinion = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('ambulance', 'user')
        ordering = ['-created']

    def __str__(self):
        return f'{self.user} → {self.ambulance} ({self.rating}★)'
