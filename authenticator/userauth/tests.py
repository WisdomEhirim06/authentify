from django.test import TestCase
import jwt
from django.contrib.auth import get_user_model
from .models import User, Organization
from datetime import time
#from rest_framework_simplejwt.settings import SIMPLE_JWT
from rest_framework.test import APIClient

SECRET_KEY = '1234567890'
class TokenGenerationTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com', password='strong_password'
        )
        self.client = APIClient()

    def test_token_generation(self):
        # Login and get access token
        response = self.client.post('/auth/login/', {'email': 'test@example.com', 'password': 'strong_password'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        token = response.data['access']

        # Decode the token and check user details
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        self.assertEqual(decoded_token['user_id'], self.user.id)
        self.assertEqual(decoded_token['email'], self.user.email)

    def test_token_expiration(self):
        # Login and get access token
        response = self.client.post('/auth/login/', {'email': 'test@example.com', 'password': 'strong_password'})
        self.assertEqual(response.status_code, 200)
        token = response.data['access']

        # Wait for token to expire (based on settings)
        #time.sleep(SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds() + 1)  # Account for some buffer time

        # Attempt to access a protected endpoint with expired token
        response = self.client.get('/api/users/me/', HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 401)  # Unauthorized


class OrganizationAccessControlTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com', password='password1'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com', password='password2'
        )
        self.org1 = Organization.objects.create(org_id='org1', name='Org 1')
        self.org2 = Organization.objects.create(org_id='org2', name='Org 2')
        self.org1.users.add(self.user1)
        self.org2.users.add(self.user2)

        self.client1 = APIClient()
        self.client1.force_authenticate(user=self.user1)
        self.client2 = APIClient()
        self.client2.force_authenticate(user=self.user2)

    def test_user_can_access_own_organizations(self):
        response = self.client1.get('/api/organisations/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['data']['organisations']), 1)
        self.assertEqual(response.data['data']['organisations'][0]['org_id'], self.org1.org_id)

        response = self.client2.get('/api/organisations/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['data']['organisations']), 1)
        self.assertEqual(response.data['data']['organisations'][0]['org_id'], self.org2.org_id)

    def test_user_cannot_access_other_users_organizations(self):
        response = self.client1.get('/api/organisations/' + self.org2.org_id + '/')
        self.assertEqual(response.status_code, 403)  # Forbidden

        response = self.client2.get('/api/organisations/' + self.org1.org_id + '/')
        self.assertEqual(response.status_code, 403)

# Create your tests here.
