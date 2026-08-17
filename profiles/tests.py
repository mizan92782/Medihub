from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import User
from profiles.models import (
    Doctor, Specialization, BloodDonor, AmbulanceProfile, PharmacyProfile, PharmacyMedicine, DiagnosticProfile, DiagnosticTest
)


class ProfilesAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Regular user
        self.regular_user = User.objects.create_user(email='user@medihub.com', password='Password123!', user_type='regular')
        
        # Doctor user
        self.doctor_user = User.objects.create_user(email='doctor@medihub.com', password='Password123!', user_type='doctor')
        self.spec = Specialization.objects.create(name_eng='Cardiology', name_bn='কার্ডিওলজি')
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            first_name='John',
            last_name='Doe',
            gender='male',
            contact_number='01700000000',
            specialization=self.spec,
            license_number='LIC12345',
            license_validity='2030-01-01'
        )

        # Pharmacy user
        self.pharmacy_user = User.objects.create_user(email='pharmacy@medihub.com', password='Password123!', user_type='pharmacy')
        self.pharmacy = PharmacyProfile.objects.create(
            user=self.pharmacy_user,
            pharmacy_name='Lazz Pharma',
            owner_name='Rahim',
            contact_number='01800000000',
            license_number='PHARM123',
            license_validity='2030-01-01'
        )

    def test_list_doctors(self):
        response = self.client.get('/profiles/doctors/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data['results'])

    def test_pharmacy_add_medicine(self):
        self.client.force_authenticate(user=self.pharmacy_user)
        response = self.client.post('/profiles/medicines/', {
            'name': 'Napa Extra',
            'generic_name': 'Paracetamol',
            'price': '15.00',
            'in_stock': True
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PharmacyMedicine.objects.count(), 1)
