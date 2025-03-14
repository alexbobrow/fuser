from rest_framework import serializers

from fuser import models


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "city",
            "country",
        ]


class UserListItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "city",
            "country",
            "is_verified",
            "balance",
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "city",
            "country",
        ]

        read_only_fields = ['id', 'username']


class UserUpdateVerificationSerializer(serializers.Serializer):
    value = serializers.BooleanField()


class UserUpdateBalanceSerializer(serializers.Serializer):
    value = serializers.IntegerField()
