from django.shortcuts import render
from .models import CustomUser, Post
from .serializers import SignUpSerializer, LoginSerializer, ProfileUpdateSerializer, PasswordChangeSerializer, PostSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import authenticate
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token 
from rest_framework import viewsets
from . import permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny


class SignUpView(APIView):
    permission_classes=[AllowAny]
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        validated_data.pop("confirmation_password")
        CustomUser.objects.create_user(**validated_data)

        return Response(
            data={
                "message":"Successfully registered🎉",
                "account":serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    permission_classes=[AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get("username")
        password = serializer.validated_data.get("password")

        user = authenticate(username=username, password=password)
        

        if user is None:
            raise ValidationError("Username yoki password noto'g'ri")

        token, created = Token.objects.get_or_create(user=user)

        return Response(
            data={
                "message":"Logged in successfully🎉",
                "user":LoginSerializer(user).data,
                "token":token.key
            },
            status=status.HTTP_200_OK
        )


class ProfileUpdateView(APIView):
    def patch(self, request):
        serializer = ProfileUpdateSerializer(instance=request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            data={
                "message":"Profile updated successfully✅",
                "profile":serializer.data
            },
            status=status.HTTP_200_OK
        )


class PasswordChangeView(APIView):
    def put(self, request):
        user = request.user
        serializer = PasswordChangeSerializer(data=request.data, context={"request":request})
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data.get("new_password")
        user.set_password(new_password)
        user.save()

        return Response(
            data={
                "message":"Password changed successfully✅"
            },
            status=status.HTTP_200_OK
        )



class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, permissions.IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)