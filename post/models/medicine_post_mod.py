from django.db import models
from django.conf import settings
from location.models import Division, District, Upozila
from core.enum import PostStatusChoices, MedicineListingTypeChoices


class MedicinePost(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='medicine_posts')

    listing_type = models.CharField(max_length=10, choices=MedicineListingTypeChoices.choices, default=MedicineListingTypeChoices.BUY)
    medicine_name = models.CharField(max_length=300)
    quantity = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    upozila = models.ForeignKey(Upozila, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.TextField(blank=True, null=True)

    contact_number = models.CharField(max_length=15)
    status = models.CharField(max_length=15, choices=PostStatusChoices.choices, default=PostStatusChoices.OPEN)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.get_listing_type_display()} {self.medicine_name} by {self.user}'
