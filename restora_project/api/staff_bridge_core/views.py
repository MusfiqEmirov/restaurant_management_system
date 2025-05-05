from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from project_apps.staff.models import Staff
from project_apps.staff.serializers import StaffSerializer
from project_apps.core.logging import get_logger

logger = get_logger(__name__)


class StaffView(APIView):
    
    def get(self, request, staff_id=None):
        """İşçi siyahısını və ya detalını qaytarır."""
        if not request.user.is_authenticated:
            logger.error(f"İcazəsiz baxış cəhdi: Qonaq")
            return Response(
                {"error": "İşçiləri görmək üçün autentifikasiya tələb olunur."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = request.user
        logger.debug(
            f"İşçi sorğusu alındı: {user.email}, ID: {staff_id}"
        )

        if staff_id:
            staff = get_object_or_404(Staff, id=staff_id, is_deleted=False)
            if user.role == "staff" and staff.user != user:
                logger.error(
                    f"İcazəsiz işçi baxışı: {user.email}, işçi ID: {staff_id}"
                )
                return Response(
                    {"error": "Yalnız öz məlumatlarınızı görə bilərsiniz."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = StaffSerializer(staff)
            logger.info(f"İşçi detalı qaytarıldı: ID {staff_id}")
            return Response(serializer.data, status=status.HTTP_200_OK)

        if user.role != "admin":
            if user.role == "staff":
                staff = get_object_or_404(Staff, user=user, is_deleted=False)
                serializer = StaffSerializer(staff)
                logger.info(f"Öz işçi məlumatları qaytarıldı: {user.email}")
                return Response(serializer.data, status=status.HTTP_200_OK)
            logger.error(
                f"İcazəsiz siyahı baxışı: {user.email}, rol: {user.role}"
            )
            return Response(
                {"error": "Yalnız adminlər işçi siyahısını görə bilər."},
                status=status.HTTP_403_FORBIDDEN,
            )

        staff_list = Staff.objects.filter(is_deleted=False)
        serializer = StaffSerializer(staff_list, many=True)
        logger.info(f"İşçi siyahısı qaytarıldı: say: {staff_list.count()}")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Yeni işçi yaradır (yalnız admin)."""
        if not request.user.is_authenticated or request.user.role != "admin":
            logger.error(
                f"İcazəsiz yaratma cəhdi: {request.user.email if request.user.is_authenticated else 'Qonaq'}, "
                f"rol: {request.user.role if request.user.is_authenticated else 'Yoxdur'}"
            )
            return Response(
                {"error": "Yalnız adminlər işçi yarada bilər."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = StaffSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            staff = serializer.save()
            logger.info(
                f"İşçi yaradıldı: ID {staff.id}, "
                f"email: {staff.user.email}, yaradan: {request.user.email}"
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Serializer xətası: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, staff_id=None):
        """İşçini yeniləyir (yalnız admin)."""
        if not staff_id:
            logger.error("İşçi ID daxil edilməyib.")
            return Response(
                {"error": "İşçi ID tələb olunur."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not request.user.is_authenticated or request.user.role != "admin":
            logger.error(
                f"İcazəsiz yeniləmə cəhdi: {request.user.email if request.user.is_authenticated else 'Qonaq'}, "
                f"rol: {request.user.role if request.user.is_authenticated else 'Yoxdur'}"
            )
            return Response(
                {"error": "Yalnız adminlər işçiləri yeniləyə bilər."},
                status=status.HTTP_403_FORBIDDEN,
            )

        staff = get_object_or_404(Staff, id=staff_id, is_deleted=False)
        serializer = StaffSerializer(
            staff, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            logger.info(
                f"İşçi yeniləndi: ID {staff.id}, "
                f"email: {staff.user.email}, yeniləyən: {request.user.email}"
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error(f"Serializer xətası: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, staff_id=None):
        """İşçini silir (yalnız admin, həqiqi silmə)."""
        if not staff_id:
            logger.error("İşçi ID daxil edilməyib.")
            return Response(
                {"error": "İşçi ID tələb olunur."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not request.user.is_authenticated or request.user.role != "admin":
            logger.error(
                f"İcazəsiz silmə cəhdi: {request.user.email if request.user.is_authenticated else 'Qonaq'}, "
                f"rol: {request.user.role if request.user.is_authenticated else 'Yoxdur'}"
            )
            return Response(
                {"error": "Yalnız adminlər işçiləri silə bilər."},
                status=status.HTTP_403_FORBIDDEN,
            )

        staff = get_object_or_404(Staff, id=staff_id, is_deleted=False)
        staff.delete()
        logger.info(
            f"İşçi həqiqi silindi: ID {staff.id}, "
            f"email: {staff.user.email}, admin: {request.user.email}"
        )
        return Response(
            {"message": "İşçi həqiqi silindi."},
            status=status.HTTP_200_OK,
        )