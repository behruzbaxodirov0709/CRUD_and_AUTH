from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='post')


urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile-update/', views.ProfileUpdateView.as_view(), name='profile-update'),
    path('password-change/', views.PasswordChangeView.as_view(), name='password-change'),


    path('', include(router.urls)),
]