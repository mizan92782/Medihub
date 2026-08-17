from django.db import models
from django.conf import settings
from location.models import District, Division, Upozila


class PharmacyProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pharmacy')
    pharmacy_name = models.CharField(max_length=200)
    owner_name = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=15)
    license_number = models.CharField(max_length=100, unique=True)
    license_validity = models.DateField()
    is_open = models.BooleanField(default=True)
    profile_dp = models.ImageField(upload_to='pharmacy/dp/', blank=True, null=True)

    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    upozila = models.ForeignKey(Upozila, on_delete=models.SET_NULL, null=True)
    address = models.TextField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.pharmacy_name} - {self.owner_name}'


class PharmacyMedicine(models.Model):
    pharmacy = models.ForeignKey(PharmacyProfile, on_delete=models.CASCADE, related_name='medicines')
    name = models.CharField(max_length=250)
    generic_name = models.CharField(max_length=250, blank=True, null=True)
    brand_name = models.CharField(max_length=250, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    stock_quantity = models.PositiveIntegerField(default=10)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='pharmacy/medicines/', blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} - {self.pharmacy.pharmacy_name} ({self.price} BDT)'
