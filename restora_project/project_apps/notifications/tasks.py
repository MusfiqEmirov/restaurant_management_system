from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum

from project_apps.accounts.models import User
from project_apps.notifications.models import (
    Notification,
    BonusPoints,
    DiscountCode,
    AdminCode,
    Message
)
from project_apps.orders.models import Order
from project_apps.core.logging import get_logger

logger = get_logger(__name__)

@shared_task
def send_discount_code_email(user_id, discount_code_id):
    try:
        user = User.objects.get(id=user_id, is_deleted=False, role="customer")
        discount_code = DiscountCode.objects.get(id=discount_code_id, is_deleted=False)
        
        # Create notification for the discount code
        notification = Notification.objects.create(
            user=user,
            title="Congratulations, you have successfully registered",
            message=(
                f"Dear {user.email},\n\n"
                f"Welcome to our restaurant! Use this code for your first order: **{discount_code.code}**\n"
                f"This code is valid for first-time orders only, and can only be used once."
                f"Thank you,\nRestaurant Team"
            ),
            sent_at=timezone.now()
        )
        discount_code.notification = notification
        discount_code.save()

        # Send email with discount code
        send_mail(
            notification.title,
            notification.message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        logger.info(f"Discount code sent: {user.email}, code: {discount_code.code}")
    except Exception as e:
        logger.error(f"Failed to send discount code: {e}")


@shared_task
def send_coffee_bonus_email(user_id):
    try:
        user = User.objects.get(id=user_id, is_deleted=False, role="customer")
        
        # Create notification for coffee bonus
        notification = Notification.objects.create(
            user=user,
            title="Congratulations! You won a coffee!",
            message=(
                f"Dear {user.email},\n\n"
                f"You earned 5 points for your purchases and have won a **free coffee** from our restaurant!\n"
                f"We look forward to serving you again!\n\n"
                f"Thank you,\nRestaurant Team"
            ),
            sent_at=timezone.now()
        )
        
        # Send email with coffee bonus notification
        send_mail(
            notification.title,
            notification.message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        logger.info(f"Coffee bonus email sent: {user.email}")
    except Exception as e:
        logger.error(f"Failed to send coffee bonus: {e}")


@shared_task
def send_admin_code_email(user_id, admin_code_id):
    try:
        user = User.objects.get(id=user_id, role="admin", is_deleted=False)
        admin_code = AdminCode.objects.get(id=admin_code_id, is_deleted=False)
        
        # Create notification for admin code
        notification = Notification.objects.create(
            user=user,
            title="Your Admin Code",
            message=(
                f"Dear {user.email},\n\n"
                f"Here is your admin code for the restaurant management system: **{admin_code.code}**\n"
                f"This code can be used to view end-of-day reports, remove drinks from a table, or modify table locations.\n\n"
                f"Thank you,\nRestaurant Team"
            ),
            sent_at=timezone.now()
        )
        admin_code.notification = notification
        admin_code.save()

        # Send admin code via email
        send_mail(
            notification.title,
            notification.message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        logger.info(f"Admin code email sent: {user.email}, code: {admin_code.code}")
    except Exception as e:
        logger.error(f"Error sending admin code: {e}")
        logger.error(f"User ID: {user_id}, Admin Code ID: {admin_code_id}")


@shared_task
def check_customer_points():
    try:
        customers = User.objects.filter(role="customer", is_deleted=False)
        
        for customer in customers:
            orders = Order.objects.filter(user=customer, is_deleted=False)
            total_spent = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            points = int(total_spent // 10)

            points_obj, _ = BonusPoints.objects.get_or_create(user=customer, is_deleted=False)

            logger.info(f"{customer.email} => Total spent: {total_spent}, Points: {points}, Last notified: {points_obj.last_notified_points}")

            new_bonus_count = points // 5
            old_bonus_count = (points_obj.last_notified_points or 0) // 5
            bonuses_to_send = new_bonus_count - old_bonus_count

            for _ in range(bonuses_to_send):
                send_coffee_bonus_email.delay(customer.id)
                logger.info(f"Coffee bonus sent: {customer.email}, points: {points}")

            if points_obj.points != points or bonuses_to_send > 0:
                points_obj.points = points
                points_obj.last_notified_points = points
                points_obj.save()

    except Exception as e:
        logger.error(f"Error while checking points: {e}")


@shared_task
def send_message_notification_email(message_id, sender_email, recipient_email, content):
    try:
        message = Message.objects.get(id=message_id, is_deleted=False)
        
        # Directly fetch the notification from the message's notification field
        notification = message.notification
        
        # If no notification is found, log an error and return
        if not notification:
            logger.error(f"No notification found for message ID: {message_id}")
            return
        
        # Send email with message notification
        send_mail(
            notification.title,
            notification.message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )
        
        logger.info(f"Message notification sent: {sender_email} -> {recipient_email}, Message ID: {message_id}")
    except Exception as e:
        logger.error(f"Failed to send message notification, Message ID: {message_id}, error: {str(e)}", exc_info=True)
