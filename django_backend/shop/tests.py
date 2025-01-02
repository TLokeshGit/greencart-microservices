from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Customer

class CustomerTests(APITestCase):
    def setUp(self):
        self.user = Customer.objects.create_user(
            email='test@example.com',
            password='Testpass123'
        )

    def test_create_customer(self):
        url = reverse('shop-api:customer-list')
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'Newpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 2)
        self.assertEqual(Customer.objects.get(email='newuser@example.com').username, 'newuser')

# ...additional test cases as needed...
