from django.test import TestCase
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import User
import hashlib


class TwoFactorAuthTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.email = "testuser@medihub.com"
        self.password = "Secr3tP@ssword123"
        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
            user_type="regular"
        )

    def tearDown(self):
        cache.clear()

    def test_standard_login_without_2fa(self):
        response = self.client.post('/authentication/auth/login/', {
            'email': self.email,
            'password': self.password
        }, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertNotIn('requires_2fa', response.data)

    def test_login_requires_2fa(self):
        # Enable 2FA
        self.user.two_factor_enabled = True
        self.user.save()

        response = self.client.post('/authentication/auth/login/', {
            'email': self.email,
            'password': self.password
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['status'])
        self.assertTrue(response.data['requires_2fa'])
        self.Bin = response.data.get('email') == self.email
        self.assertEqual(response.data['email'], self.email)
        self.assertNotIn('access', response.data)

        # Check that OTP is cached in Redis
        otp_key = hashlib.sha256(f'auth:login_2fa:{self.email}'.encode()).hexdigest()
        cached_otp = cache.get(otp_key)
        self.assertIsNotNone(cached_otp)

    def test_verify_2fa_success(self):
        # Setup 2FA OTP in cache
        self.user.two_factor_enabled = True
        self.user.save()

        # Cache valid OTP hash
        otp_code = "123456"
        otp_key = hashlib.sha256(f'auth:login_2fa:{self.email}'.encode()).hexdigest()
        cache.set(otp_key, hashlib.sha256(otp_code.encode()).hexdigest(), timeout=300)

        response = self.client.post('/authentication/auth/verify-2fa/', {
            'email': self.email,
            'otp': otp_code
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['status'])
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        # Check OTP key is deleted after successful verification
        self.assertIsNone(cache.get(otp_key))

    def test_verify_2fa_invalid_otp(self):
        # Setup 2FA OTP in cache
        self.user.two_factor_enabled = True
        self.user.save()

        otp_key = hashlib.sha256(f'auth:login_2fa:{self.email}'.encode()).hexdigest()
        cache.set(otp_key, hashlib.sha256("123456".encode()).hexdigest(), timeout=300)

        response = self.client.post('/authentication/auth/verify-2fa/', {
            'email': self.email,
            'otp': "999999" # invalid OTP
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_toggle_2fa(self):
        # Force authentication
        self.client.force_authenticate(user=self.user)

        response = self.client.post('/authentication/auth/toggle-2fa/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['two_factor_enabled'])

        # Refresh from db and assert
        self.user.refresh_from_db()
        self.assertTrue(self.user.two_factor_enabled)

        # Toggle again (disable)
        response = self.client.post('/authentication/auth/toggle-2fa/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['two_factor_enabled'])

        self.user.refresh_from_db()
        self.assertFalse(self.user.two_factor_enabled)
