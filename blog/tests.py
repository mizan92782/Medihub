from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import User
from profiles.models import Doctor, Specialization
from blog.models import BlogPost


class BlogAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.doctor_user = User.objects.create_user(email='doctorblog@medihub.com', password='Password123!', user_type='doctor')
        self.spec = Specialization.objects.create(name_eng='Neurology', name_bn='নিউরোলজি')
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            first_name='Dr. Karim',
            last_name='Uddin',
            gender='male',
            contact_number='01811112222',
            specialization=self.spec,
            license_number='DOC999',
            license_validity='2030-01-01'
        )

    def test_doctor_create_blog_post(self):
        self.client.force_authenticate(user=self.doctor_user)
        response = self.client.post('/blogs/posts/', {
            'title': 'Understanding Migraine Symptoms and Treatments',
            'content': 'Migraine headaches can be triggered by stress, sleep deprivation...',
            'category': 'neurology',
            'status': 'published'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BlogPost.objects.count(), 1)
