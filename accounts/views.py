from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    MyTokenObtainPairSerializer,
    RegisterSerializer,
    UserMeSerializer,
    UserPublicSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Cadastro de novo usuário. Endpoint público."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(TokenObtainPairView):
    """Login: recebe username/password, devolve tokens JWT + dados do usuário."""

    serializer_class = MyTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    """Ver/editar o próprio perfil (usuário autenticado)."""

    serializer_class = UserMeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserDetailView(generics.RetrieveAPIView):
    """Ver o perfil público de qualquer usuário."""

    queryset = User.objects.all()
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = "username"


class FollowToggleView(APIView):
    """Seguir/deixar de seguir um usuário (POST alterna o estado)."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, username):
        target = User.objects.filter(username=username).exclude(pk=request.user.pk).first()
        if not target:
            return Response({"detail": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        if request.user.following.filter(pk=target.pk).exists():
            request.user.following.remove(target)
            following_now = False
        else:
            request.user.following.add(target)
            following_now = True

        return Response(
            {
                "following": following_now,
                "followers_count": target.followers_count,
            }
        )
