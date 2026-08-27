from unittest.mock import patch
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from forecasting.models import EnergyPrediction

User = get_user_model()

class ForecastingViewsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tester', 
            email='test@example.com', 
            password='secretpassword'
        )
        self.client.force_authenticate(user=self.user)
        
        self.energy_prediction = EnergyPrediction.objects.create(
            user=self.user, category='load', hour=12, day=1, 
            month=1, dayofweek=1, lag_1=100.0, lag_24=105.0
        )

    @patch('forecasting.views.predict_energy.delay')
    @patch('forecasting.views.send_prediction_email.delay')
    def test_energy_predict_api_view_post(self, mock_email, mock_predict):
        """
        Test that posting valid data creates a prediction, triggers Celery tasks, 
        and returns a 202 Accepted status.
        """
        url = reverse('forecasting:predict_energy') 
        data = {
            'category': 'load', 'hour': 12, 'day': 1, 
            'month': 1, 'dayofweek': 1, 'lag_1': 100.0, 'lag_24': 105.0
        }
        
        response = self.client.post(url, data, format='json')
        
        # Verify prediction was created
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn("id", response.data)
        
        # Verify background tasks were queued
        self.assertTrue(mock_predict.called)
        self.assertTrue(mock_email.called)

    def test_prediction_history_list_view_default(self):
        """Test that the history view defaults to filtering 'all' if no type is passed."""
        url = reverse('forecasting:history') 
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['filter_type'], 'all')

    def test_energy_prediction_detail_view(self):
        """Test that detail view correctly retrieves instance and injects domain context."""
        url = reverse('forecasting:energy_detail', kwargs={'pk': self.energy_prediction.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['domain'], 'energy')