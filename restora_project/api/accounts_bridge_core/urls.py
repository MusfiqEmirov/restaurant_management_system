from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView
                                            )
from .views import (RegisterView,
                    ProfileAPIView,
                    ProfileDetailAPIView, 
                    CustomTokenObtainPairView,
                    LogoutView,
                    AdminUserCreateView
                    )

urlpatterns = [
    path('accounts/register/', RegisterView.as_view(), name='register'),
    path('accounts/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('accounts/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('accounts/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),

    path('accounts/admin/users/', AdminUserCreateView.as_view(), name='admin_user_create'),
    path('accounts/profiles/', ProfileAPIView.as_view(), name='profile_list'),
    path('accounts/profiles/<int:id>/', ProfileDetailAPIView.as_view(), name='profile_detail'),
]