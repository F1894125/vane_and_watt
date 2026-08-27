from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from datetime import date
from account.models import Profile

User = get_user_model()

class ProfileModelTest(TestCase):
    def setUp(self):
        # Setting up a test user
        self.user = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='secretpassword'
        )
        # Creating a profile to test model methods
        self.profile = Profile.objects.create(
            user=self.user,
            date_of_birth=date(1995, 5, 5)
        )

    def test_profile_string_representation(self):
        """Test to check the custom __str__ method on the Profile model."""
        self.assertEqual(str(self.profile), f'Profile for user {self.user.username}')

    def test_profile_get_absolute_url(self):
        """Test to check if the canonical API URL returns correctly."""
        expected_url = reverse('account:profile_form', kwargs={'username': self.user.username})
        self.assertEqual(self.profile.get_absolute_url(), expected_url)