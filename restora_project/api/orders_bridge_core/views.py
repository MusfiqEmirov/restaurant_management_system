from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum

from project_apps.orders.models import Order, OrderItem
from project_apps.orders.serializers import (OrderSerializer,
                                             OrderItemSerializer,
                                             SalesReportSerializer
                                            )
from project_apps.core.logging import get_logger

logger = get_logger(__name__)


class OrderView(APIView):
    # Viewing, updating, deleting, and creating order details

    def get(self, request, order_id=None):
        # If the user is not authenticated
        if not request.user.is_authenticated:
            logger.error(f"Permission required to view orders")
            return Response(
                {"error": "Login is required to view orders"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = request.user
        logger.debug(
            f"Order query received: {user.email}, ID: {order_id}, "
            f"parameters: {request.query_params}"
        )

        if order_id:
            order = get_object_or_404(Order, id=order_id, is_deleted=False)
            if user.role == "customer" and order.user != user:
                logger.error(
                    f"Admin or staff role required to view order: {user.email}, order ID: {order_id}"
                )
                return Response(
                    {"error": "Only customers can view their own orders"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = OrderSerializer(order)
            logger.info(f"Order details returned: ID {order_id}")
            return Response(serializer.data, status=status.HTTP_200_OK)

        orders = Order.objects.filter(is_deleted=False)
        # If the user is a customer
        if user.role == "customer":
            orders = orders.filter(user=user)
        # If the user is an admin
        elif user.role == "admin" and request.query_params:
            filter_serializer = SalesReportSerializer(data=request.query_params)
            if filter_serializer.is_valid():
                start_date = filter_serializer.validated_data.get("start_date")
                end_date = filter_serializer.validated_data.get("end_date")
                payment_type = filter_serializer.validated_data.get("payment_type")

                # Filter by start date
                if start_date:
                    orders = orders.filter(created_at__date__gte=start_date)
                # Filter by end date
                if end_date:
                    orders = orders.filter(created_at__date__lte=end_date)
                # Filter by payment type
                if payment_type:
                    orders = orders.filter(payment_type=payment_type)
            else:
                logger.error(f"Filter validation error: {filter_serializer.errors}")
                return Response(
                    filter_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )

        serializer = OrderSerializer(orders, many=True)
        logger.info(f"List of orders returned: count: {orders.count()}")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # Orders can only be created by admins or staff
        if not request.user.is_authenticated:
            logger.error(f"Unauthorized attempt to create: Guest")
            return Response(
                {"error": "Login is required to create orders"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if request.user.role not in ["admin", "staff"]:
            logger.error(
                f"Permission required for login: {request.user.email}, role: {request.user.role}"
            )
            return Response(
                {"error": "Only admins and staff can create orders"},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data.copy()

        # If the customer ID is not provided
        if "user_id" not in data:
            logger.error(f"Customer ID not provided: {request.user.email}")
            return Response(
                {"error": "Customer ID is required to create an order."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data["created_by_id"] = request.user.id

        serializer = OrderSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            order = serializer.save()
            logger.info(
                f"Order created: ID {order.id}, "
                f"customer: {order.user.email}, created by: {request.user.email}"
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Serializer error: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, order_id=None):
        # Orders can only be updated by admins or staff
        if not order_id:
            logger.error("Order ID not provided")
            return Response(
                {"error": "Order ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not request.user.is_authenticated or request.user.role not in ["admin", "staff"]:
            logger.error(
                f"Permission required to update: {request.user.email if request.user.is_authenticated else 'Guest'}, "
                f"role: {request.user.role if request.user.is_authenticated else 'None'}"
            )
            return Response(
                {"error": "Only admins or staff can update orders"},
                status=status.HTTP_403_FORBIDDEN,
            )

        order = get_object_or_404(Order, id=order_id, is_deleted=False)
        serializer = OrderSerializer(
            order, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            logger.info(
                f"Order updated: ID {order.id}, "
                f"customer: {order.user.email}, updated by: {request.user.email}"
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error(f"Serializer error: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, order_id=None):
        # Only admin can delete
        if not order_id:
            logger.error("Order not provided")
            return Response(
                {"error": "Order ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not request.user.is_authenticated or request.user.role not in ["admin", "staff"]:
            logger.error(
                f"Permission required to delete: {request.user.email if request.user.is_authenticated else 'Guest'}, "
                f"role: {request.user.role if request.user.is_authenticated else 'None'}"
            )
            return Response(
                {"error": "Only admins can delete orders"},
                status=status.HTTP_403_FORBIDDEN,
            )

        order = get_object_or_404(Order, id=order_id, is_deleted=False)
        if request.user.role == "admin":
            order.delete()
            logger.info(
                f"Order permanently deleted: ID {order.id}, "
                f"customer: {order.user.email}, admin: {request.user.email}"
            )
            return Response(
                {"message": "Order permanently deleted"},
                status=status.HTTP_200_OK,
            )
        else:  # staff
            order.is_deleted = True
            order.save()
            logger.info(
                f"Order soft deleted: ID {order.id}, "
                f"customer: {order.user.email}, staff: {request.user.email}"
            )
            return Response(
                {"message": "Order soft deleted."},
                status=status.HTTP_200_OK,
            )


class OrderItemView(APIView):
    # Listing, updating, deleting, and creating order items

    def get(self, request, item_id=None):
        # Returning the list of order items
        if not request.user.is_authenticated:
            logger.error(f"Permission required: Guest")
            return Response(
                {"error": "Login required to view order items"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = request.user
        logger.debug(
            f"Order item query received: {user.email}, ID: {item_id}"
        )

        if item_id:
            item = get_object_or_404(OrderItem, id=item_id, is_deleted=False)
            if user.role == "customer" and item.order.user != user:
                logger.error(
                    f"Cannot view others' orders: {user.email}, item ID: {item_id}"
                )
                return Response(
                    {"error": "You can only view your own orders."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = OrderItemSerializer(item)
            logger.info(f"Order item details returned: ID {item_id}")
            return Response(serializer.data, status=status.HTTP_200_OK)

        items = OrderItem.objects.filter(is_deleted=False)
        
        if user.role == "customer":
            items = items.filter(order__user=user)
        serializer = OrderItemSerializer(items, many=True)
        logger.info(f"List of order items returned: count: {items.count()}")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # Creating new order item only by admins or staff
        if not request.user.is_authenticated:
            logger.error(f"Permission required for customer: Guest")
            return Response(
                {"error": "Login required to create order items"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if request.user.role not in ["admin", "staff"]:
            logger.error(
                f"Permission required for login: {request.user.email}, role: {request.user.role}"
            )
            return Response(
                {"error": "Only admins and staff can create order items"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = OrderItemSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            item = serializer.save()
            logger.info(
                f"Order item created: ID {item.id}, "
                f"menu item: {item.menu_item.name}, created by: {request.user.email}"
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Serializer error: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, item_id=None):
        # Updating order items only by admins or staff
        if not item_id:
            logger.error("Order item ID is required")
            return Response(
                {"error": "Order item ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not request.user.is_authenticated or request.user.role not in ["admin", "staff"]:
            logger.error(
                f"Permission required to update: {request.user.email if request.user.is_authenticated else 'Guest'}, "
                f"role: {request.user.role if request.user.is_authenticated else 'None'}"
            )
            return Response(
                {"error": "Only admins or staff can update order items."},
                status=status.HTTP_403_FORBIDDEN,
            )

        item = get_object_or_404(OrderItem, id=item_id, is_deleted=False)
        serializer = OrderItemSerializer(
            item, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            logger.info(
                f"Order item updated: ID {item.id}, "
                f"menu item: {item.menu_item.name}, updated by: {request.user.email}"
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error(f"Serializer error: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, item_id=None):
        # Deleting order items by admin or staff
        if not item_id:
            logger.error("Order item ID not provided")
            return Response(
                {"error": "Order item ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not request.user.is_authenticated or request.user.role not in ["admin", "staff"]:
            logger.error(
                f"Permission required to delete: {request.user.email if request.user.is_authenticated else 'Guest'}, "
                f"role: {request.user.role if request.user.is_authenticated else 'None'}"
            )
            return Response(
                {"error": "Only admins or staff can delete order items."},
                status=status.HTTP_403_FORBIDDEN,
            )

        item = get_object_or_404(OrderItem, id=item_id, is_deleted=False)
        if request.user.role == "admin":
            item.delete()
            logger.info(
                f"Order item deleted: ID {item.id}, "
                f"menu item: {item.menu_item.name}, admin: {request.user.email}"
            )
            return Response(
                {"message": "Order item deleted"},
                status=status.HTTP_200_OK,
            )
        else:  # staff
            item.is_deleted = True
            item.save()
            logger.info(
                f"Order item soft deleted: ID {item.id}, "
                f"menu item: {item.menu_item.name}, staff: {request.user.email}"
            )
            return Response(
                {"message": "Order item soft deleted"},
                status=status.HTTP_200_OK,
            )


class SalesReportView(APIView):
    # Viewing and filtering sales reports

    def get(self, request):
        # Returning the sales report
        if not request.user.is_authenticated or request.user.role != "admin":
            logger.error(
                f"Permission required to view report: {request.user.email if request.user.is_authenticated else 'Guest'}, "
                f"role: {request.user.role if request.user.is_authenticated else 'None'}"
            )
            return Response(
                {"error": "Only admins can view sales reports"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = SalesReportSerializer(data=request.query_params)
        if not serializer.is_valid():
            logger.error(f"Report serializer error {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        start_date = data["start_date"]
        end_date = data["end_date"]
        payment_type = data.get("payment_type")

        orders = Order.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            is_deleted=False,
        )
        if payment_type:
            orders = orders.filter(payment_type=payment_type)

        total_amount = orders.aggregate(Sum("total_amount"))["total_amount__sum"] or 0
        order_count = orders.count()
        total_bonus_points = sum(order.calculate_bonus_points() for order in orders)

        report_data = {
            "start_date": start_date,
            "end_date": end_date,
            "payment_type": payment_type,
            "orders": OrderSerializer(orders, many=True).data,
            "total_amount": total_amount,
            "order_count": order_count,
            "total_bonus_points": total_bonus_points,
        }

        logger.info(
            f"Sales report prepared for date range {start_date} - {end_date}, "
            f"payment type: {payment_type or 'all'}, admin: {request.user.email}"
        )
        return Response(report_data, status=status.HTTP_200_OK)
