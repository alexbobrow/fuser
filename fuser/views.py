from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from fuser import serializers
from fuser.models import User
from fuser.permissions import IsOwner


class UserListView(CreateModelMixin, ListModelMixin, GenericAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['username', 'is_verified']
    authentication_classes= [BasicAuthentication]
    queryset = User.objects.all()

    def get_serializer_class(self):
        return serializers.UserListItemSerializer if self.request.method == 'GET' else serializers.UserCreateSerializer

    def get_permissions(self):
        return {
            "POST": [],
            "GET": [IsAdminUser()],
            "OPTIONS": [],
        }[self.request.method]

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class UserDetailView(UpdateModelMixin, DestroyModelMixin, GenericAPIView):
    serializer_class = serializers.UserUpdateSerializer
    authentication_classes = [BasicAuthentication]
    queryset = User.objects.all()

    def get_permissions(self):
        staff = IsAdminUser()
        staff_or_owner = (IsAdminUser | IsOwner)()
        res = {
            "GET": [staff],
            "PUT": [staff_or_owner],
            "PATCH": [staff_or_owner],
            "DELETE": [staff],
            "OPTIONS": [],
        }[self.request.method]
        return res

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class UserUpdateVerificationView(GenericAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    serializer_class = serializers.UserUpdateVerificationSerializer

    def post(self, request, *args, **kwargs):
        ser = serializers.UserUpdateVerificationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        instance = self.get_object()
        instance.is_verified = ser.validated_data["value"]
        instance.save()
        return Response(ser.data, status=status.HTTP_200_OK)


class UserUpdateBalanceView(GenericAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAdminUser]
    serializer_class = serializers.UserUpdateBalanceSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        ser = serializers.UserUpdateBalanceSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        instance = User.objects.select_for_update().get(id=kwargs["pk"])
        if not instance.is_verified:
            raise ValidationError({"detail": "User not verified"})
        instance.balance += ser.validated_data["value"]
        instance.save()
        return Response(dict(value=instance.balance), status=status.HTTP_200_OK)
