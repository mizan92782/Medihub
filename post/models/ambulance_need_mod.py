from django.db import models
from django.conf import settings
from location.models import Division, District, Upozila
from core.enum import AmbulanceTypeChoices, PostStatusChoices, UrgencyChoices

class AmbulanceNeedPost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ambulance_need_posts')

    ambulance_type = models.CharField(max_length=20, choices=AmbulanceTypeChoices.choices)
    
    # Location
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    upozila = models.ForeignKey(Upozila, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.TextField(blank=True, null=True)

    # When needed
    needed_date = models.DateField()
    needed_time = models.TimeField()

    # Contact
    contact_number = models.CharField(max_length=15)

    urgency = models.CharField(max_length=10, choices=UrgencyChoices.choices, default=UrgencyChoices.HIGH)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=15, choices=PostStatusChoices.choices, default=PostStatusChoices.OPEN)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.ambulance_type} ambulance needed at {self.address or self.district}'
