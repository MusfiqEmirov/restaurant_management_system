from django.urls import path
from rest_framework_simplejwt.views import (
                                            TokenRefreshView
                                            )
from .views import (RegisterView,
                    ProfileAPIView,
                    ProfileDetailAPIView, 
                    LoginView,
                    LogoutView,
                    AdminUserCreateView
                    )

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('admin/users/', AdminUserCreateView.as_view(), name='admin_user_create'),
    path('profiles/', ProfileAPIView.as_view(), name='profile_list'),
    path('profiles/<int:id>/', ProfileDetailAPIView.as_view(), name='profile_detail'),
]