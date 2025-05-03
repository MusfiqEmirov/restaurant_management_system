from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum

from project_apps.accounts.models import User
from project_apps.notifications.models import Notification, BonusPoints, DiscountCode, AdminCode
from project_apps.orders.models import Order
from project_apps.core.logging import get_logger
logging = get_logger(__name__)

@shared_task
def send_discount_code_email(user_id, discount_code_id):
    try:
        from project_apps.accounts.models import User
        user = User.objects.get(id=user_id, is_deleted=False, role="customer")
        discount_code = DiscountCode.objects.get(id=discount_code_id, is_deleted=False)
        notification = Notification.objects.create(
            user=user,
            title="Tebrikler siz artiq hesab acdiniz",
            message=(
                f"Hormetli {user.email},\n\n"
                f"Reatranimiza xow geldiniz! Ilk sifarisde istfade etmek ucun codunuz:**{discount_code.code}**\n"
                f"Bu kod bir defelikdir ve ancaq ilk sifarisde kecerlidir"
                f"tesekkur ediirik\nRestaran komandasi"
            ),
            sent_at=timezone.now()
        )
        discount_code.notification = notification
        discount_code.save()
        send_mail(
            notification.title,
            notification.message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        logging.info(f"endirim kodu gonderildi:{user.email},kod:{discount_code.code}")
    except Exception as e:
        logging.error(f"endrim kodu gonderilmedi xeta:{e}")

@shared_task
def send_coffee_bonus_email(user_id):
    try:
        from project_apps.accounts.models import User
        user = User.objects.get(id=user_id, is_deleted=False, role="customer")
        notification = Notification.objects.create(
            user=user,
            title="Təbrikler! Kofe qazandiniz!",
            message=(
                f"Hormetli  {user.email},\n\n"
                f"Alis-verislerinize gore 5 xal topladinniz və retaranimiz terefinnen **pulsuz kofe** qazanadiniz!\n"
                f"sizi yeniden gozleyirik!\n\n"
                f"Tesekkurler,\nRestoran komandasi"
            ),
            sent_at=timezone.now()
        )
        send_mail(
            notification.title,
            notification.message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        logging.info(f"Kofe bonusu maila gonderildi: {user.email}")
    except Exception as e:
        logging.error(f"kofe bonusu gonderilmedi xeta:{e}")

@shared_task
def send_admin_code_email(user_id, admin_code_id):
    try:
        from project_apps.accounts.models import User
        user = User.objects.get(id=user_id, role="admin", is_deleted=False)
        admin_code = AdminCode.objects.get(id=admin_code_id, is_deleted=False)
        notification = Notification.objects.create(
            user=user,
            title="Admin kodunuz",
            message=(
                f"Hormetli {user.email},\n\n"
                f"Restoran idareetme sistemi ucun icaze  kodunuz: **{admin_code.code}**\n"
                f"Bu kodu gun sonu hesabatlarina baxmaq, masadan icki silmek və ya yer deyiwdirmek kimi emeliyyatlar ucun istifade ede bilersiniz.\n\n"
                f"Tesekkurler,\nRestoran komandasi"
            ),
            sent_at=timezone.now()
        )
        admin_code.notification = notification
        admin_code.save()
        
        # Email gönderimi
        send_mail(
            notification.title,
            notification.message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        logging.info(f"Admin kodu maile gonderildi: {user.email}, kod: {admin_code.code}")
    except Exception as e:
        logging.error(f"admin kodu gonderilemde xeta bas verdi.xeta:{e}")
        logging.error(f"User ID: {user_id}, Admin Code ID: {admin_code_id}")

@shared_task
def check_customer_points():
    try:
        customers = User.objects.filter(role="customer", is_deleted=False)
        
        for customer in customers:
            orders = Order.objects.filter(user=customer, is_deleted=False)
            total_spent = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            points = int(total_spent // 10)

            points_obj, _ = BonusPoints.objects.get_or_create(user=customer, is_deleted=False)

            logging.info(f"{customer.email} => Total spent: {total_spent}, Points: {points}, Last notified: {points_obj.last_notified_points}")

            new_bonus_count = points // 5
            old_bonus_count = (points_obj.last_notified_points or 0) // 5
            bonuses_to_send = new_bonus_count - old_bonus_count

            for _ in range(bonuses_to_send):
                send_coffee_bonus_email.delay(customer.id)
                logging.info(f"Kofe bonusu gonderildi: {customer.email}, xal: {points}")

            if points_obj.points != points or bonuses_to_send > 0:
                points_obj.points = points
                points_obj.last_notified_points = points
                points_obj.save()

    except Exception as e:
        logging.error(f"Xal yoxlanisi zamani xeta: {e}")

