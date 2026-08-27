from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from forecasting.serializers import EnergyPredictionSerializer

User = get_user_model()

class ForecastingSerializersTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tester', 
            password='secretpassword'
        )
        # Serializers require a request context to extract the user
        self.factory = APIRequestFactory()
        self.request = self.factory.post('/')
        self.request.user = self.user 

    def test_energy_prediction_serializer_creates_instance(self):
        """Test that the serializer properly attaches the user from context upon creation."""
        data = {
            'category': 'load',
            'hour': 12, 'day': 1, 'month': 1, 'dayofweek': 1,
            'lag_1': 100.0, 'lag_24': 105.0
        }
        
        serializer = EnergyPredictionSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        
        instance = serializer.save()
        
        self.assertEqual(instance.user, self.user)
        self.assertEqual(instance.category, 'load')