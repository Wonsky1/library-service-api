from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.serializers import UserSerializer, DetailUserSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = DetailUserSerializer



class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)

    def get_object(self):
        return self.request.user
