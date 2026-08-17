from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import User
from post.models import BloodNeedPost, MedicineNeedPost, EquipmentNeedPost, GeneralPost


class PostAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='poster@medihub.com', password='Password123!', user_type='regular')
        self.client.force_authenticate(user=self.user)

    def test_create_blood_need_post(self):
        response = self.client.post('/posts/blood-need/', {
            'patient_name': 'Anisur Rahman',
            'patient_age': 35,
            'patient_gender': 'male',
            'blood_group': 'A+',
            'bags_needed': 2,
            'hospital_name': 'Dhaka Medical College Hospital',
            'needed_date': '2026-08-15',
            'needed_time': '10:00:00',
            'contact_number': '01711112222',
            'urgency': 'critical'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BloodNeedPost.objects.count(), 1)

    def test_create_general_post(self):
        response = self.client.post('/posts/general/', {
            'title': 'Emergency Medical Helpline Assistance',
            'content': 'Providing free ambulance hotline support during rainy season.',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(GeneralPost.objects.count(), 1)
