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
    # List, detail, creation, update, and deletion of customers.
    permission_classes = [IsAuthenticated]

    def get(self, request, customer_id=None):
        # Returns the customer list or details.
        user = request.user
        logger.debug(
            f"Customer request received: {user.email}, ID: {customer_id}"
        )

        if customer_id:
            customer = get_object_or_404(User, id=customer_id, is_deleted=False, role="customer")
            if user.role == "customer" and customer != user:
                logger.error(
                    f"Unauthorized customer view attempt: {user.email}, customer ID: {customer_id}"
                )
                return Response(
                    {"error": "You can only view your own data."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = UserSerializer(customer)
            logger.info(f"Customer details returned: ID {customer_id}")
            return Response(serializer.data, status=status.HTTP_200_OK)

        if user.role not in ["admin", "staff"]:
            customer = get_object_or_404(User, id=user.id, is_deleted=False, role="customer")
            serializer = UserSerializer(customer)
            logger.info(f"Own customer data returned: {user.email}")
            return Response(serializer.data, status=status.HTTP_200_OK)

        customers = User.objects.filter(is_deleted=False, role="customer")
        serializer = UserSerializer(customers, many=True)
        logger.info(f"Customer list returned: count: {customers.count()}")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # Creates a new customer (only admin).
        if request.user.role != "admin":
            logger.error(
                f"Unauthorized creation attempt: {request.user.email}, role: {request.user.role}"
            )
            return Response(
                {"error": "Only admins can create customers."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = UserSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            customer = serializer.save(role="customer")
            logger.info(
                f"Customer created: ID {customer.id}, email: {customer.email}"
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Serializer error: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, customer_id=None):
        # Updates a customer.
        if not customer_id:
            logger.error("Customer ID not provided.")
            return Response(
                {"error": "Customer ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = request.user
        customer = get_object_or_404(User, id=customer_id, is_deleted=False, role="customer")
        if user.role == "customer" and customer != user:
            logger.error(
                f"Unauthorized update attempt: {user.email}, customer ID: {customer_id}"
            )
            return Response(
                {"error": "You can only update your own data."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if user.role not in ["admin", "customer"]:
            logger.error(
                f"Unauthorized update attempt: {user.email}, role: {user.role}"
            )
            return Response(
                {"error": "Only admins or customers can update."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = UserSerializer(
            customer, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            logger.info(
                f"Customer updated: ID {customer.id}, email: {customer.email}"
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error(f"Serializer error: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, customer_id=None):
        """Deletes a customer (only admin)."""
        if not customer_id:
            logger.error("Customer ID not provided.")
            return Response(
                {"error": "Customer ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.user.role != "admin":
            logger.error(
                f"Unauthorized deletion attempt: {request.user.email}, role: {request.user.role}"
            )
            return Response(
                {"error": "Only admins can delete customers."},
                status=status.HTTP_403_FORBIDDEN,
            )

        customer = get_object_or_404(User, id=customer_id, is_deleted=False, role="customer")
        customer.delete()
        logger.info(
            f"Customer deleted: ID {customer.id}, email: {customer.email}"
        )
        return Response(
            {"message": "Customer deleted."},
            status=status.HTTP_200_OK,
        )


class CustomerDiscountCodeView(APIView):
    """Checking discount codes (70% and 20%)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Checks the discount code."""
        if request.user.role != "customer":
            logger.error(
                f"Unauthorized discount code attempt: {request.user.email}, role: {request.user.role}"
            )
            return Response(
                {"error": "Only customers can use discount codes."},
                status=status.HTTP_403_FORBIDDEN,
            )

        code = request.data.get("code")
        if not code:
            logger.error(f"Discount code not provided: {request.user.email}")
            return Response(
                {"error": "Discount code is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        discount = DiscountCode.objects.filter(
            code=code, user=request.user, is_deleted=False, is_used=False
        ).first()
        if not discount:
            logger.error(f"Invalid discount code: {request.user.email}, code: {code}")
            return Response(
                {"error": "Discount code is invalid or already used."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        discount_percentage = 20.00
        if discount.notification and discount.notification.title == "70% Discount on First Order":
            if Order.objects.filter(user=request.user, is_deleted=False).exists():
                logger.error(f"Not the first order: {request.user.email}")
                return Response(
                    {"error": "The 70% discount code is only valid for the first order."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            discount_percentage = 70.00

        logger.info(f"Discount code accepted: {request.user.email}, code: {code}")
        return Response(
            {
                "message": "Discount code accepted. Use it when placing an order.",
                "code": code,
                "discount_percentage": discount_percentage
            },
            status=status.HTTP_200_OK
        )


class BonusRedeemView(APIView):
    """Free coffee with bonus points."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Requests a free coffee gift."""
        if request.user.role != "customer":
            logger.error(
                f"Unauthorized spend attempt: {request.user.email}, role: {request.user.role}"
            )
            return Response(
                {"error": "Only customers can redeem bonus points."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = request.user
        action = request.data.get("action")
        if action != "coffee":
            logger.error(f"Invalid action: {user.email}, action: {action}")
            return Response(
                {"error": "The action must be 'coffee'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        bonus_points = BonusPoints.objects.filter(user=user, is_deleted=False).first()
        total_points = bonus_points.points if bonus_points else 0
        if total_points < 5:
            logger.error(
                f"Not enough points: {user.email}, points: {total_points}"
            )
            return Response(
                {"error": "At least 5 points are required for a free coffee."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        BonusTransaction.objects.create(
            user=user,
            points=-5,
            description="Free coffee gift",
            order=None
        )
        bonus_points.points -= 5
        bonus_points.save()
        logger.info(
            f"Free coffee gift: customer: {user.email}, points: -5"
        )
        return Response(
            {"message": "Free coffee gift successfully redeemed."},
            status=status.HTTP_200_OK,
        )
