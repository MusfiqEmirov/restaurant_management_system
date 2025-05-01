from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .models import Notification, DiscountCode, AdminCode, BonusPoints
from project_apps.core.logging import get_logger

logging = get_logger(__name__)

@shared_task
def send_discount_code_email(user_id, discount_code_id):
    try:
        from project_apps.accounts.models import User
        user = User.objects.get(id=user_id, is_delete=False, role="customer")
        discount_code = DiscountCode.objects.get(id=discount_code_id, is_delete=False)
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
        user = User.objects.get(id=user_id, is_delete=False, role="customer")
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
        user = User.objects.get(id=user_id, is_staff=True, is_delete=False)
        admin_code = AdminCode.objects.get(id=admin_code_id, is_delete=False)
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
        send_mail(
            notification.title,
            notification.message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        logging.info(f"Admin kodu maile gonderildi: {user.email}, kod: {admin_code.code}")
    except Exception  as e:
        logging.error(f"admin kodu gonderilemde xeta bas verdi.xeta:{e}")

@shared_task
def check_customer_points():
    try:
        from project_apps.accounts.models import User
        customers = User.objects.filter(role="customer", is_delete=False)
        for customer in customers:
            points_obj, _ = BonusPoints.objects.get_or_create(user=customer, is_delete=False)
            if points_obj.points >= 5 and points_obj.points > points_obj.last_notified_points:
                send_coffee_bonus_email.delay(customer.id)
                points_obj.last_notified_points = points_obj.points
                points_obj.save()
                logging.info(f"Kofe bonusu test edildi və gonderildi: {customer.email}")
    except Exception as e:
        logging.error(f"Xal yoxlanisi zamnai xeta: {e}")