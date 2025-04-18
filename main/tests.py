from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import UserProfile, LoginLog


class UserProfileTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword123"
        )
        self.client = Client()

    def test_profile_creation(self):
        """Test that a user profile is created automatically"""
        self.assertTrue(hasattr(self.user, "profile"))
        self.assertIsInstance(self.user.profile, UserProfile)

    def test_profile_view(self):
        """Test that logged in user can view their profile"""
        self.client.login(username="testuser", password="testpassword123")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/profile.html")

    def test_profile_edit(self):
        """Test that a user can edit their profile"""
        self.client.login(username="testuser", password="testpassword123")

        # Test GET request
        response = self.client.get(reverse("profile_edit"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/profile_edit.html")

        # Test POST request
        data = {
            "username": "testuser",
            "email": "updated@example.com",
            "first_name": "Test",
            "last_name": "User",
            "address": "123 Test St",
            "phone_number": "+1234567890",
            "latitude": 45.0,
            "longitude": -75.0,
        }
        response = self.client.post(reverse("profile_edit"), data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Refresh user from database
        self.user.refresh_from_db()

        # Check if the profile has been updated
        self.assertEqual(self.user.email, "updated@example.com")
        self.assertEqual(self.user.first_name, "Test")
        self.assertEqual(self.user.profile.address, "123 Test St")
        self.assertEqual(self.user.profile.phone_number, "+1234567890")
        self.assertEqual(self.user.profile.latitude, 45.0)
        self.assertEqual(self.user.profile.longitude, -75.0)

    def test_login_required(self):
        """Test that login is required to access profile pages"""
        # Test without login
        response = self.client.get(reverse("profile"))
        self.assertNotEqual(response.status_code, 200)

        response = self.client.get(reverse("profile_edit"))
        self.assertNotEqual(response.status_code, 200)


class MapTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword123"
        )
        # Set location for the user
        self.user.profile.latitude = 45.0
        self.user.profile.longitude = -75.0
        self.user.profile.save()

        # Create a superuser
        self.superuser = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpassword123"
        )
        self.superuser.profile.latitude = 45.0
        self.superuser.profile.longitude = -75.0
        self.superuser.profile.save()

        self.client = Client()

    def test_map_view(self):
        """Test that the map view works"""
        self.client.login(username="testuser", password="testpassword123")
        response = self.client.get(reverse("map"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/map.html")

    def test_get_user_locations(self):
        """Test the user locations API"""
        self.client.login(username="testuser", password="testpassword123")
        response = self.client.get(reverse("user_locations"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)  # 2 users in the database

        # Check the first user data
        first_user = next(u for u in data if u["username"] == "testuser")
        self.assertEqual(first_user["latitude"], 45.0)
        self.assertEqual(first_user["longitude"], -75.0)

    def test_user_popup_permission(self):
        """Test that users can only view their own profile popup"""
        # Test normal user viewing their own profile
        self.client.login(username="testuser", password="testpassword123")
        response = self.client.get(reverse("user_popup", args=[self.user.id]))
        self.assertEqual(response.status_code, 200)

        # Test normal user viewing someone else's profile
        response = self.client.get(reverse("user_popup", args=[self.superuser.id]))
        self.assertEqual(response.status_code, 403)

        # Test superuser viewing someone else's profile
        self.client.login(username="admin", password="adminpassword123")
        response = self.client.get(reverse("user_popup", args=[self.user.id]))
        self.assertEqual(response.status_code, 200)


class LoginLogTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword123"
        )
        self.client = Client()

    def test_login_log_creation(self):
        """Test that login events are logged"""
        # Count login logs before login
        before_count = LoginLog.objects.count()

        # Log in
        self.client.login(username="testuser", password="testpassword123")

        # Count login logs after login
        after_count = LoginLog.objects.count()
        self.assertEqual(after_count, before_count + 1)

        # Check the log entry
        log = LoginLog.objects.latest("timestamp")
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, "login")

    def test_logout_log_creation(self):
        """Test that logout events are logged"""
        # Login first
        self.client.login(username="testuser", password="testpassword123")

        # Count login logs before logout
        before_count = LoginLog.objects.count()

        # Log out
        self.client.logout()

        # Count login logs after logout
        after_count = LoginLog.objects.count()
        self.assertEqual(after_count, before_count + 1)

        # Check the log entry
        log = LoginLog.objects.latest("timestamp")
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, "logout")
