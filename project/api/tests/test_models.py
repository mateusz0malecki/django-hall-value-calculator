from rest_framework.test import APITestCase
from api.models import User


class TestModel(APITestCase):

    def test_creates_user(self):
        user = User.objects.create_user(
            username='admin',
            email='admin@admin.com',
            password='admin123'
        )
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, 'admin@admin.com')
        self.assertFalse(user.is_staff)

    def test_creates_superuser(self):
        user = User.objects.create_superuser(
            username='admin',
            email='admin@admin.com',
            password='admin123'
        )
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, 'admin@admin.com')
        self.assertTrue(user.is_staff)

    def test_raises_error_when_no_username(self):
        self.assertRaises(
            ValueError,
            User.objects.create_user,
            username="",
            email='admin@admin.com',
            password='admin123'
        )

    def test_raises_message_when_no_email(self):
        with self.assertRaisesMessage(
            ValueError,
            'The given email must be set'
        ):
            User.objects.create_user(
                username='admin',
                email='',
                password='admin123'
            )

    def test_create_superuser_staff_status(self):
        with self.assertRaisesMessage(
            ValueError,
            'Superuser must have is_staff=True.',
        ):
            User.objects.create_superuser(
                username='admin',
                email='admin@admin.com',
                password='admin123',
                is_staff=False
            )

    def test_create_superuser_super_user_status(self):
        with self.assertRaisesMessage(
            ValueError,
            'Superuser must have is_superuser=True.',
        ):
            User.objects.create_superuser(
                username='admin',
                email='admin@admin.com',
                password='admin123',
                is_superuser=False
            )
