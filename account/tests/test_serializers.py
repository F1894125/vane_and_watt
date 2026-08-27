from django.test import TestCase
from rest_framework.exceptions import ValidationError
from datetime import date, timedelta
from account.serializers import RegistrationSerializer

class RegistrationSerializerTest(TestCase):
    def setUp(self):
        self.serializer = RegistrationSerializer()
        self.today = date.today()

    def test_valid_first_name(self):
        """Test to check if a valid first name passes the regex validation."""
        self.assertEqual(self.serializer.validate_first_name("Alice"), "Alice")

    def test_invalid_date_of_birth_underage(self):
        """Test to check if a user under 18 raises a validation error."""
        underage_dob = self.today - timedelta(days=15*365) # Approx 15 years old
        with self.assertRaises(ValidationError):
            self.serializer.validate_date_of_birth(underage_dob)

    def test_passwords_do_not_match(self):
        """Test the general validate method to ensure mismatched passwords fail."""
        attrs = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password1': 'Secure@123',
            'password2': 'Different@123'
        }
        with self.assertRaises(ValidationError) as context:
            self.serializer.validate(attrs)
        
        # DRF exceptions usually wrap error strings in lists/dicts inside the exception string
        self.assertIn('Passwords do not match.', str(context.exception))