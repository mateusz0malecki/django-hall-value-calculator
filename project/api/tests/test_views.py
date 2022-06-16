from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from api.models import Hall


class APITestHallHelper(APITestCase):
    def create_hall(self):
        hall = {
            "salesman": 1,
            "length": 5,
            "width": 5,
            "pole_height": 5,
            "roof_slope": 7,
        }
        response = self.client.post(reverse('halls-list'), hall)
        return response

    def authenticate(self):
        self.client.post(reverse('register'), {
            'username': 'test',
            'email': 'test@test.com',
            'password': 'test'
        })
        response = self.client.post(reverse('login'), {
            'username': 'test',
            'email': 'test@test.com',
            'password': 'test'
        })
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['token']}")


class TestHallViewSet(APITestHallHelper):

    def test_fail_create_hall_with_no_auth(self):
        response = self.create_hall()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_hall(self):
        hall_count = Hall.objects.all().count()
        self.authenticate()
        response = self.create_hall()
        self.assertEqual(hall_count+1, Hall.objects.all().count())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['roof_slope'], 7)

    def test_retrieve_all_halls(self):
        self.authenticate()
        response = self.client.get(reverse('halls-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['results'], list)

    def test_get_one_hall(self):
        self.authenticate()
        helper = self.create_hall()
        response = self.client.get(f"/api/halls/{helper.data['project_id']}")
        hall = Hall.objects.get(project_id=helper.data['project_id'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(hall.roof_slope, response.data['roof_slope'])

    def test_delete_one_hall(self):
        self.authenticate()
        helper = self.create_hall()
        prev_db_count = Hall.objects.count()
        response = self.client.delete(f"/api/halls/{helper.data['project_id']}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(prev_db_count, Hall.objects.count()+1)

    def test_update_one_hall(self):
        self.authenticate()
        helper = self.create_hall()
        response = self.client.put(f"/api/halls/{helper.data['project_id']}", {
            'length': 10,
            'width': 10,
            'pole_height': 10,
            'roof_slope': 10,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Hall.objects.get(project_id=helper.data['project_id']).roof_slope, 10)

    def test_create_hall_invalid_serializer(self):
        self.authenticate()
        hall = {
            "salesman": 1,
            "length": 5,
            "width": 5,
            "pole_height": 5,
        }
        response = self.client.post(reverse('halls-list'), hall)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_one_hall_invalid_serializer(self):
        self.authenticate()
        helper = self.create_hall()
        response = self.client.put(f"/api/halls/{helper.data['project_id']}", {
            'length': 10,
            'width': 10,
            'pole_height': 10,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
