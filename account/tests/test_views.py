from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

# Import your token generator
from account.tokens import create_token 

User = get_user_model()

class AuthenticationViewsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='secretpassword'
        )
        self.login_url = reverse('account:login') 
        self.logout_url = reverse('account:logout')
        self.register_url = reverse('account:register')

        # Generate real tokens for the test user
        self.access_token = create_token(self.user.id, 'a')
        self.refresh_token = create_token(self.user.id, 'r')

    def authenticate_client(self):
        """Helper method to inject valid JWT cookies into the test client."""
        self.client.cookies['access_token'] = self.access_token
        self.client.cookies['refresh_token'] = self.refresh_token

    def test_authenticated_user_redirected_from_login(self):
        """Test to check if logged-in users are redirected away from the login form."""
        self.authenticate_client() # Use cookies instead of force_authenticate
        response = self.client.get(self.login_url)
        
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, reverse('account:dashboard'))

    def test_authenticated_user_redirected_from_registration(self):
        """Test to check if logged-in users are redirected away from the registration form."""
        self.authenticate_client() # Use cookies instead of force_authenticate
        response = self.client.get(self.register_url)
        
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, reverse('account:dashboard'))

    def test_logout_clears_cookies_and_redirects(self):
        """Test to check if the logout view purges tokens and redirects appropriately."""
        self.authenticate_client() # Sets REAL tokens so jwt.decode() doesn't crash
        
        response = self.client.get(self.logout_url)
        
        # Verify the redirect to the login page
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, self.login_url)
        
        # Django clears cookies by resetting their values to empty strings
        self.assertEqual(response.cookies['access_token'].value, '')
        self.assertEqual(response.cookies['refresh_token'].value, '')