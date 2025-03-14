from copy import copy

from rest_framework import status
from rest_framework.test import APITestCase

from fuser import models


class UserListViewTests(APITestCase):
    def setUp(self):
        self.url = "/user/"

    def test_create_success(self):
        data = {
            "email": "test@example.com",
            "username": "fuser",
            "first_name": "first_name",
            "last_name": "last_name",
            "city": "city",
            "country": "country",
        }
        response = self.client.post(self.url, data=data, format="json")
        response_json = response.json()
        data["id"] = response_json["id"]
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_json, data)
        user = models.User.objects.get(id=response_json["id"])
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.username, "fuser")
        self.assertEqual(user.first_name, "first_name")
        self.assertEqual(user.last_name, "last_name")
        self.assertEqual(user.city, "city")
        self.assertEqual(user.country, "country")

    def test_create_success_no_optional_fields(self):
        data = {
            "username": "fuser",
        }
        response = self.client.post(self.url, data=data, format="json")
        response_json = response.json()
        expected_response = {
            "id": response_json[ "id"],
            "email": "",
            "username": "fuser",
            "first_name": "",
            "last_name": "",
            "city": "",
            "country": "",
        }
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_json, expected_response)
        user = models.User.objects.get(id=response_json["id"])
        self.assertEqual(user.email, "")
        self.assertEqual(user.username, "fuser")
        self.assertEqual(user.first_name, "")
        self.assertEqual(user.last_name, "")
        self.assertEqual(user.city, "")
        self.assertEqual(user.country, "")

    def test_create_fail_empty_username(self):
        data = {
            "username": "",
        }
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_json = response.json()
        expected_response = {'username': ['This field may not be blank.']}
        self.assertEqual(response_json, expected_response)

    def test_create_fail_no_username(self):
        data = {
            "email": "test@example.com",
        }
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_json = response.json()
        expected_response = {'username': ['This field is required.']}
        self.assertEqual(response_json, expected_response)

    def test_create_fail_username_occupied(self):
        models.User.objects.create(username="fuser")
        data = {
            "username": "fuser",
        }
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_json = response.json()
        expected_response = {'username': ['user with this Username already exists.']}
        self.assertEqual(response_json, expected_response)

    def test_list_base(self):
        user1 = models.User.objects.create(username="foo", is_staff=True)
        user2 = models.User.objects.create(username="bar")
        user3 = models.User.objects.create(username="baz", is_verified=True)

        # Not staff
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user1)

        expected_response = [
            {
                'id': user1.id, 'username': 'foo', 'email': '', 'first_name': '', 'last_name': '',
                'city': '', 'country': '', 'balance': 0, 'is_verified': False
            },
            {
                'id': user2.id, 'username': 'bar', 'email': '', 'first_name': '', 'last_name': '',
                'city': '', 'country': '', 'balance': 0, 'is_verified': False
            },
            {
                'id': user3.id, 'username': 'baz', 'email': '', 'first_name': '', 'last_name': '',
                'city': '', 'country': '', 'balance': 0, 'is_verified': True
            },
        ]

        # All entries
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = sorted(response.json(), key=lambda k: k['id'])
        self.assertEqual(response_json, expected_response)

        # Filtered by username
        response = self.client.get(self.url, data=dict(username="bar"))
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json, [expected_response[1]])

        # Filtered by verified positive
        response = self.client.get(self.url, data=dict(is_verified="1"))
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json, [expected_response[2]])

        # Filtered by verified negative
        response = self.client.get(self.url, data=dict(is_verified="0"))
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json, expected_response[:-1])


class UserDetailViewTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.staff = models.User.objects.create(username="foo", is_staff=True)
        cls.user = models.User.objects.create(username="bar")
        cls.wrong_user = models.User.objects.create(username="baz")
        cls.new_email = "test@example.com"
        cls.put_data = {
            "email": cls.new_email,
            "username": "user",
            "first_name": "first_name",
            "last_name": "last_name",
            "city": "city",
            "country": "country",
        }
        cls.patch_data = {
            "email": cls.new_email,
        }
        cls.expected_patch_response = {
            "id": cls.user.id,
            "email": cls.new_email,
            "username": "bar",
            "first_name": "",
            "last_name": "",
            "city": "",
            "country": "",
        }
        cls.url = f"/user/{cls.user.id}"

    def setUp(self):
        self.user.refresh_from_db()

    def test_put_by_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url, data=self.put_data, format="json")
        response_json = response.json()
        self.user.refresh_from_db()
        expected_data = copy(self.put_data)
        expected_data.update(id=self.user.id, username=self.user.username)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json, expected_data)
        for field, value in expected_data.items():
            self.assertEqual(getattr(self.user, field), value, field)

    def test_put_by_staff(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.put(self.url, data=self.put_data, format="json")
        response_json = response.json()
        self.user.refresh_from_db()
        expected_data = copy(self.put_data)
        expected_data.update(id=self.user.id, username=self.user.username)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json, expected_data)
        for field, value in expected_data.items():
            self.assertEqual(getattr(self.user, field), value, field)

    def test_put_by_nobody(self):
        response = self.client.put(self.url, data=self.put_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_by_wrong_user(self):
        self.client.force_authenticate(user=self.wrong_user)
        response = self.client.put(self.url, data=self.put_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_by_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url, data=self.patch_data, format="json")
        response_json = response.json()
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json, self.expected_patch_response)
        self.user.refresh_from_db()
        for field, value in self.expected_patch_response.items():
            self.assertEqual(getattr(self.user, field), value, field)

    def test_patch_by_staff(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.put(self.url, data=self.patch_data, format="json")
        response_json = response.json()
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json, self.expected_patch_response)
        self.user.refresh_from_db()
        for field, value in self.expected_patch_response.items():
            self.assertEqual(getattr(self.user, field), value, field)

    def test_patch_by_nobody(self):
        response = self.client.patch(self.url, data=self.patch_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_by_wrong_user(self):
        self.client.force_authenticate(user=self.wrong_user)
        response = self.client.patch(self.url, data=self.patch_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_by_staff(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.delete(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(models.User.DoesNotExist):
            self.user.refresh_from_db()

    def test_delete_by_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_by_nobody(self):
        response = self.client.delete(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserUpdateVerificationViewTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.staff = models.User.objects.create(username="staff", is_staff=True)

    def test_verify(self):
        self.client.force_authenticate(user=self.staff)
        unverified_user = models.User.objects.create(username="user", is_verified=False)
        url = f"/user/{unverified_user.id}/update-verification"
        response = self.client.post(url, data={"value": True}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        unverified_user.refresh_from_db()
        self.assertTrue(unverified_user.is_verified)

    def test_unverify(self):
        self.client.force_authenticate(user=self.staff)
        verified_user = models.User.objects.create(username="user", is_verified=True)
        url = f"/user/{verified_user.id}/update-verification"
        response = self.client.post(url, data={"value": False}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        verified_user.refresh_from_db()
        self.assertFalse(verified_user.is_verified)

    def test_no_permission(self):
        user = models.User.objects.create(username="user")
        self.client.force_authenticate(user=user)
        url = "/user/1/update-verification"
        response = self.client.post(url, data={"value": False}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_authorized(self):
        url = "/user/1/update-verification"
        response = self.client.post(url, data={"value": False}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserUpdateBalanceViewTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.staff = models.User.objects.create(username="staff", is_staff=True)

    def test_top_up(self):
        self.client.force_authenticate(user=self.staff)
        user = models.User.objects.create(username="user", is_verified=True, balance=50)
        url = f"/user/{user.id}/update-balance"
        response = self.client.post(url, data={"value": 100}, format="json")
        response_json = response.json()
        user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_value = 150
        self.assertEqual(response_json, {"value": expected_value})
        self.assertEqual(user.balance, expected_value)

    def test_charge(self):
        self.client.force_authenticate(user=self.staff)
        user = models.User.objects.create(username="user", is_verified=True, balance=150)
        url = f"/user/{user.id}/update-balance"
        response = self.client.post(url, data={"value": -100}, format="json")
        response_json = response.json()
        expected_value = 50
        user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json, {"value": expected_value})
        self.assertEqual(user.balance, expected_value)

    def test_not_verified(self):
        self.client.force_authenticate(user=self.staff)
        user = models.User.objects.create(username="user")
        url = f"/user/{user.id}/update-balance"
        response = self.client.post(url, data={"value": 100}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_json = response.json()
        self.assertEqual(response_json, {'detail': 'User not verified'})

    def test_no_permission(self):
        user = models.User.objects.create(username="user")
        self.client.force_authenticate(user=user)
        url = f"/user/{user.id}/update-balance"
        response = self.client.post(url, data={"value": 100}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_authorized(self):
        url = "/user/1/update-balance"
        response = self.client.post(url, data={"value": 100}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
