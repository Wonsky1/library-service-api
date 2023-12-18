from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.serializers import UserSerializer, DetailUserSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = DetailUserSerializer

    @extend_schema(
        description="Register a new user",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)

    def get_object(self):
        return self.request.user

    @extend_schema(
        description="Get info about your account (For authenticated users)",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        description="Fully update user by id (For authenticated users)",
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        description="Partial update user by id (For authenticated users)",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
