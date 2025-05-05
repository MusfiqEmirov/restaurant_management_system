from django.shortcuts import get_object_or_404
from django.db.models import Sum

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from project_apps.accounts.models import User
from project_apps.accounts.serializers import UserSerializer
from project_apps.notifications.models import DiscountCode, BonusPoints
from project_apps.customers.models import BonusTransaction
from project_apps.core.logging import get_logger
from project_apps.orders.models import Order

logger = get_logger(__name__)


class CustomerView(APIView):
    # Müştərilərin siyahısı, detalı, yaradılması, yenilənməsi və silinməsi.
    permission_classes = [IsAuthenticated]

    def get(self, request, customer_id=None):
        # Müştəri siyahısını və ya detalını qaytarır.
        user = request.user
        logger.debug(
            f"Müştəri sorğusu alındı: {user.email}, ID: {customer_id}"
        )

        if customer_id:
            customer = get_object_or_404(User, id=customer_id, is_deleted=False, role="customer")
            if user.role == "customer" and customer != user:
                logger.error(
                    f"İcazəsiz müştəri baxışı: {user.email}, müştəri ID: {customer_id}"
                )
                return Response(
                    {"error": "Yalnız öz məlumatlarınızı görə bilərsiniz."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = UserSerializer(customer)
            logger.info(f"Müştəri detalı qaytarıldı: ID {customer_id}")
            return Response(serializer.data, status=status.HTTP_200_OK)

        if user.role not in ["admin", "staff"]:
            customer = get_object_or_404(User, id=user.id, is_deleted=False, role="customer")
            serializer = UserSerializer(customer)
            logger.info(f"Öz müştəri məlumatları qaytarıldı: {user.email}")
            return Response(serializer.data, status=status.HTTP_200_OK)

        customers = User.objects.filter(is_deleted=False, role="customer")
        serializer = UserSerializer(customers, many=True)
        logger.info(f"Müştəri siyahısı qaytarıldı: say: {customers.count()}")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # Yeni müştəri yaradır (yalnız admin).
        if request.user.role != "admin":
            logger.error(
                f"İcazəsiz yaratma cəhdi: {request.user.email}, rol: {request.user.role}"
            )
            return Response(
                {"error": "Yalnız adminlər müştəri yarada bilər."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = UserSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            customer = serializer.save(role="customer")
            logger.info(
                f"Müştəri yaradıldı: ID {customer.id}, email: {customer.email}"
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Serializer xətası: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, customer_id=None):
        # Müştərini yeniləyir.
        if not customer_id:
            logger.error("Müştəri ID daxil edilməyib.")
            return Response(
                {"error": "Müştəri ID tələb olunur."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = request.user
        customer = get_object_or_404(User, id=customer_id, is_deleted=False, role="customer")
        if user.role == "customer" and customer != user:
            logger.error(
                f"İcazəsiz yeniləmə cəhdi: {user.email}, müştəri ID: {customer_id}"
            )
            return Response(
                {"error": "Yalnız öz məlumatlarınızı yeniləyə bilərsiniz."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if user.role not in ["admin", "customer"]:
            logger.error(
                f"İcazəsiz yeniləmə cəhdi: {user.email}, rol: {user.role}"
            )
            return Response(
                {"error": "Yalnız admin və ya müştəri yeniləyə bilər."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = UserSerializer(
            customer, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            logger.info(
                f"Müştəri yeniləndi: ID {customer.id}, email: {customer.email}"
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error(f"Serializer xətası: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, customer_id=None):
        """Müştərini silir (yalnız admin)."""
        if not customer_id:
            logger.error("Müştəri ID daxil edilməyib.")
            return Response(
                {"error": "Müştəri ID tələb olunur."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.user.role != "admin":
            logger.error(
                f"İcazəsiz silmə cəhdi: {request.user.email}, rol: {request.user.role}"
            )
            return Response(
                {"error": "Yalnız adminlər müştəriləri silə bilər."},
                status=status.HTTP_403_FORBIDDEN,
            )

        customer = get_object_or_404(User, id=customer_id, is_deleted=False, role="customer")
        customer.delete()
        logger.info(
            f"Müştəri silindi: ID {customer.id}, email: {customer.email}"
        )
        return Response(
            {"message": "Müştəri silindi."},
            status=status.HTTP_200_OK,
        )


class CustomerDiscountCodeView(APIView):
    """Endirim kodlarının yoxlanılması (70% və 20%)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Endirim kodunu yoxlayır."""
        if request.user.role != "customer":
            logger.error(
                f"İcazəsiz endirim kodu cəhdi: {request.user.email}, rol: {request.user.role}"
            )
            return Response(
                {"error": "Yalnız müştərilər endirim kodu istifadə edə bilər."},
                status=status.HTTP_403_FORBIDDEN,
            )

        code = request.data.get("code")
        if not code:
            logger.error(f"Endirim kodu daxil edilməyib: {request.user.email}")
            return Response(
                {"error": "Endirim kodu tələb olunur."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        discount = DiscountCode.objects.filter(
            code=code, user=request.user, is_deleted=False, is_used=False
        ).first()
        if not discount:
            logger.error(f"Endirim kodu yanlışdır: {request.user.email}, kod: {code}")
            return Response(
                {"error": "Endirim kodu yanlışdır və ya istifadə olunub."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        discount_percentage = 20.00
        if discount.notification and discount.notification.title == "İlk Sifarişə 70% Endirim":
            if Order.objects.filter(user=request.user, is_deleted=False).exists():
                logger.error(f"İlk sifariş deyil: {request.user.email}")
                return Response(
                    {"error": "70% endirim kodu yalnız ilk sifariş üçün keçərlidir."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            discount_percentage = 70.00

        logger.info(f"Endirim kodu qəbul olundu: {request.user.email}, kod: {code}")
        return Response(
            {
                "message": "Endirim kodu qəbul olundu. Sifariş yaradarkən istifadə edin.",
                "code": code,
                "discount_percentage": discount_percentage
            },
            status=status.HTTP_200_OK
        )


class BonusRedeemView(APIView):
    """Bonus xalları ilə kofe hədiyyəsi."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Kofe hədiyyəsi tələb edir."""
        if request.user.role != "customer":
            logger.error(
                f"İcazəsiz xərcləmə cəhdi: {request.user.email}, rol: {request.user.role}"
            )
            return Response(
                {"error": "Yalnız müştərilər bonus xallarını xərcləyə bilər."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = request.user
        action = request.data.get("action")
        if action != "coffee":
            logger.error(f"Yanlış aksiya: {user.email}, aksiya: {action}")
            return Response(
                {"error": "Aksiya 'coffee' olmalıdır."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        bonus_points = BonusPoints.objects.filter(user=user, is_deleted=False).first()
        total_points = bonus_points.points if bonus_points else 0
        if total_points < 5:
            logger.error(
                f"Kifayət qədər xal yoxdur: {user.email}, xallar: {total_points}"
            )
            return Response(
                {"error": "Pulsuz kofe üçün minimum 5 xal tələb olunur."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        BonusTransaction.objects.create(
            user=user,
            points=-5,
            description="Pulsuz kofe hədiyyəsi",
            order=None
        )
        bonus_points.points -= 5
        bonus_points.save()
        logger.info(
            f"Pulsuz kofe hədiyyəsi: müştəri: {user.email}, xallar: -5"
        )
        return Response(
            {"message": "Pulsuz kofe hədiyyəsi uğurla əldə edildi."},
            status=status.HTTP_200_OK,
        )