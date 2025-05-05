import uuid
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.db import transaction

from project_apps.accounts.models import User, Profile
from project_apps.accounts.serializers import (UserSerializer,
                                               RegisterSerializer,
                                               ProfileSerializer,
                                               LoginSerializer,
                                               AdminUserCreateSerializer
                                               )

# Set up logger for tracking logs
logger = logging.getLogger(__name__)

# Register View - Handle User Registration
class RegisterView(APIView):
    permission_classes = [AllowAny]  # Public access, anyone can register

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Create a new user
                with transaction.atomic():
                    user = serializer.save()

                    # Generate JWT tokens
                    refresh = RefreshToken.for_user(user)
                    token_data = {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }

                    logger.info(f"New user registered: {user.email}")
                    return Response({
                        "user": UserSerializer(user).data,
                        "token": token_data,  # Return the token data to the user
                        "message": "Registration successful"
                    }, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error during registration: {str(e)}", exc_info=True)
                return Response({"error": "Error during registration"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Profile View - Handle Access to User Profiles
class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access

    def get(self, request):
        """
        If the user is an admin, they can see all profiles. 
        Regular users can only see their own profile.
        """
        user = request.user
        if user.role == "admin":
            profiles = Profile.objects.filter(is_deleted=False)
            serializer = ProfileSerializer(profiles, many=True)
        else:
            profile = get_object_or_404(Profile, user=user, is_deleted=False)
            serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request):
        """
        Create a new profile. 
        Admin can create accounts for both admins and users.
        """
        serializer = ProfileSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save()
                logger.info(f"New profile created: {request.user.email}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error creating profile: {str(e)}", exc_info=True)
                return Response({'error': 'Error during profile creation'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Profile Detail View - Handle Access, Update and Delete for Individual Profiles
class ProfileDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access

    def get(self, request, id):
        """
        View a profile.
        Admin can view any profile.
        Regular users can only view their own profile.
        """
        profile = get_object_or_404(Profile, id=id, is_deleted=False)
        user = request.user
        if user.role != 'admin' and profile.user != user:
            return Response({'error': 'You do not have permission to view this profile'},
                            status=status.HTTP_403_FORBIDDEN
                            )
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def patch(self, request, id):
        """
        Update a profile.
        Admin can update any profile.
        Regular users can only update their own profile.
        """
        profile = get_object_or_404(Profile, id=id, is_deleted=False)
        user = request.user
        if user.role != 'admin' and profile.user != user:
            return Response({'error': 'You do not have permission to update this profile'},
                            status=status.HTTP_403_FORBIDDEN
                            )
        serializer = ProfileSerializer(profile, data=request.data,
                                       partial=True,
                                       context={'request': request}
                                       )
        if serializer.is_valid():
            try:
                serializer.save()
                logger.info(f"Profile updated: {profile.user.email}")
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error updating profile: {str(e)}", exc_info=True)
                return Response({'error': 'Error during profile update'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def delete(self, request, id):
        """
        Soft delete a profile.
        Admin can delete any profile.
        Regular users can only delete their own profile.
        """
        profile = get_object_or_404(Profile, id=id, is_deleted=False)
        user = request.user
        if user.role != 'admin' and profile.user != user:
            return Response({'error': 'You do not have permission to delete this profile'},
                             status=status.HTTP_403_FORBIDDEN)
        try:
            profile.delete()  # Soft delete functionality
            logger.info(f"Profile deleted: {profile.user.email}")
            return Response({'message': 'Profile successfully deleted.'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error deleting profile: {str(e)}", exc_info=True)
            return Response({'error': 'Error during profile deletion'},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Login View - Handle User Login
class LoginView(APIView):
    permission_classes = [AllowAny]  # Public access, anyone can log in

    def post(self, request):
        """
        Login using email and password.
        """
        logger.debug(f"Login request received successfully {request.data}")
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.validated_data['user']
                refresh = RefreshToken.for_user(user)
                token_data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
                logger.info(f"User logged in: {user.email}")
                return Response({
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'username': user.username,
                        'role': user.role
                    },
                    'tokens': token_data
                }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Login error: {str(e)}", exc_info=True)
                return Response({'error': 'Error during login'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                                )
        logger.error(f"Serializer error: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Logout View - Handle User Logout
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can log out

    def post(self, request):
        """
        Log out the user by adding the refresh token to the blacklist.
        """
        logger.debug(f"Logout request received: {request.data}")
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                logger.error("Refresh token not provided.")
                return Response({"error": "Refresh token is required."},
                                status=status.HTTP_400_BAD_REQUEST
                                )

            token = RefreshToken(refresh_token)
            token.blacklist()  # Add the token to the blacklist to invalidate it
            logger.info(f"User logged out: {request.user.email}")
            return Response({"message": "Successfully logged out"},
                            status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            logger.error(f"Logout error: {str(e)}", exc_info=True)
            return Response({"error": f"Error during logout: {str(e)}"},
                            status=status.HTTP_400_BAD_REQUEST
                            )

# Admin User Creation View - Handle Creation of New Users by Admins
class AdminUserCreateView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access

    def post(self, request):
        """
        Admin can create new users.
        Only users with the 'admin' role can create users.
        Email, username, password, role, first_name, last_name, phone_number, and address are required.
        """
        if request.user.role != "admin":
            return Response({"error": "Only admins can create users"},
                            status=status.HTTP_403_FORBIDDEN
                            )

        serializer = AdminUserCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                    logger.info(f"Admin created new user: {user.email}, role: {user.role}")
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error creating user: {str(e)}", exc_info=True)
                return Response({"error": "Error during user creation."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
