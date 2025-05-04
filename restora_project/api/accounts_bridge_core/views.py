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

logger = logging.getLogger(__name__)

class RegisterView(APIView):
    permission_classes = [AllowAny]  # public, hər kəs qeydiyyatdan keçə bilər

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Yeni istifadəçi yaratmaq
                with transaction.atomic():
                    user = serializer.save()

                    # Token yaratmaq
                    refresh = RefreshToken.for_user(user)
                    token_data = {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }

                    logger.info(f"Yeni istifadəçi qeydiyyatdan keçdi: {user.email}")
                    return Response({
                        "user": UserSerializer(user).data,
                        "token": token_data,  # Token məlumatlarını istifadəçiyə qaytarırıq
                        "message": "Qeydiyyat uğurla tamamlandı"
                    }, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Qeydiyyat zamanı xəta baş verdi: {str(e)}", exc_info=True)
                return Response({"error": "Qeydiyyat zamanı xəta baş verdi"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        admin eger varsa ve giriw edibse profilleri elde ede baxa biler
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
    yeni profil yaratmag
    admin admin ucun ve musteri ucun hesab yarada biler
    """
    serializer = ProfileSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        try:
            serializer.save()
            logger.info(f"yeni  profil yaradildi: {request.user.email}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"profil yaratma xetasi: {str(e)}", exc_info=True)
            return Response({'error': 'profil yaratma zamani xeta bas verdi'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        """
        profile baxmag
        admin istenilen profile baxa biler
        musterinistenilen prpfile baxa biler
        """
        profile = get_object_or_404(Profile, id=id, is_deleted=False)
        user = request.user
        if user.role != 'admin' and profile.user != user:
            return Response({'error': 'bu profile baxmag icazeniz yoxdur'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def patch(self, request, id):
        """
        profili yenilemek
        -admin istenilen profili yenileye biler
        musteri yalnis oz profilini yenileye biler
        """
        profile = get_object_or_404(Profile, id=id, is_deleted=False)
        user = request.user
        if user.role != 'admin' and profile.user != user:
            return Response({'error': 'bu profiliyenilemk icazeniz yoxdur'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProfileSerializer(profile, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save()
                logger.info(f"profil yenilendi: {profile.user.email}")
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"profil yenileme xetasi: {str(e)}", exc_info=True)
                return Response({'error': 'profil yenileme xetasi'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def delete(self, request, id):
        """
        profili silmek(sof_delete olaraq ama)
        admin istenilen profili siler biler
        musteri yalnis oz profilini sile biler
        """
        profile = get_object_or_404(Profile, id=id, is_deleted=False)
        user = request.user
        if user.role != 'admin' and profile.user != user:
            return Response({'error': 'Bu profili silmek icazeniz yoxdur'}, status=status.HTTP_403_FORBIDDEN)
        try:
            profile.delete()  # SoftDeleteMixin ile isleyir
            logger.info(f"profil silindi: {profile.user.email}")
            return Response({'message': 'profil ugurla silindi.'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"profil silme xetasi: {str(e)}", exc_info=True)
            return Response({'error': 'profil silme zamani xeta bas verdi '}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        email ve ya parol ile giris
        """
        logger.debug(f"login sorgusu ugurla alindi {request.data}")
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.validated_data['user']
                refresh = RefreshToken.for_user(user)
                token_data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
                logger.info(f"user daxil oldu {user.email}")
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
                logger.error(f"login xetasi {str(e)}", exc_info=True)
                return Response({'error': 'giris zamani xeta bas verdi'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.error(f"Serializer xetasi: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        User üçün logout. Refresh token-i qara siyahıya əlavə edir.
        """
        logger.debug(f"Logout sorğusu alındı: {request.data}")
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                logger.error("Refresh token daxil edilməyib.")
                return Response({"error": "Refresh token tələb olunur."}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info(f"User çıxış etdi: {request.user.email}")
            return Response({"message": "ugurla cixis olundu"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            logger.error(f"Logout xətası: {str(e)}", exc_info=True)
            return Response({"error": f"Çıxış zamanı xəta baş verdi: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        
class AdminUserCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        admin terefden yeni user yaratmag
        ancaq rolesi admin olan
        giris email username, password,role, first_name, last_name, phone_number, address
        email signals ile mesaj gedir
        """
        if request.user.role != "admin":
            return Response({"error": "yalniz adminler user yarada biler"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = AdminUserCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                    logger.info(f"admin yeni user yaratdi: {user.email}, role: {user.role}")
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"User yaratma xetasi: {str(e)}", exc_info=True)
                return Response({"error": "User yaratma zamani xeta bas verdi."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        