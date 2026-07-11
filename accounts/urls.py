from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("me/", views.MeView.as_view(), name="me"),
    path("users/<str:username>/", views.UserDetailView.as_view(), name="user-detail"),
    path("users/<str:username>/follow/", views.FollowToggleView.as_view(), name="user-follow"),
]
