from rest_framework import serializers
from django.db.models import Sum
from django.utils import timezone
import uuid


from project_apps.customers.models import BonusTransaction
from project_apps.notifications.models import BonusPoints
from .models import Order, OrderItem
from project_apps.accounts.models import User
from project_apps.accounts.serializers import UserSerializer
from project_apps.menu.serializers import MenuItemSerializer
from project_apps.menu.models import MenuItem
from project_apps.core.constants import STATUS_CHOICES, PAYMENT_TYPE_CHOICES
from project_apps.notifications.models import DiscountCode, Notification
from project_apps.core.logging import get_logger

logger = get_logger(__name__)


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    menu_item_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.filter(is_available=True, is_deleted=False),
        source="menu_item",
        write_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "menu_item",
            "menu_item_id",
            "quantity",
            "price",
            "created_at",
            "updated_at",
            "is_deleted",
        ]
         # ancaq oxuna biler deyiwdirile bilmez
        read_only_fields = [ 
            "id",
            "created_at",
            "updated_at",
            "is_deleted"
        ]
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("say hemiwe musbet olmalidir")
        return value
    
    
        

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_deleted=False, role="customer"),
        source="user",
        write_only=True
    )
    created_by = UserSerializer(read_only=True)
    created_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_deleted=False, role__in=["admin", "staff"]),
        source="created_by",
        write_only=True,
        required=False,
        allow_null=True,
    )
    order_items = OrderItemSerializer(many=True)
    bonus_points = serializers.IntegerField(
        source="calculate_bonus_points", 
        read_only=True
    )
    discount_code = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "user_id",
            "created_by",
            "created_by_id",
            "total_amount",
            "status",
            "payment_type",
            "order_items",
            "bonus_points",
            "created_at",
            "updated_at",
            "is_deleted",
            "discount_code",
        ]
         # ancaq oxuna biler deyiwdirile bilmez
        read_only_fields = [ 
            "id",
            "created_at",
            "updated_at",
            "is_deleted"
        ]
    
    def validate_status(self, value):
        valid_statuses = [choice[0] for choice in STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError("yalniw status deyeri")
        return value

    def validate_payment_type(self, value):
        valid_payment_types = [choice[0] for choice in PAYMENT_TYPE_CHOICES]
        if value not in valid_payment_types:
            raise serializers.ValidationError("yalniw odenis novu daxil etdiniz")
        return value
    
    def create(self, validated_data):
        from project_apps.notifications.tasks import send_email_task
        from django.conf import settings

        order_items_data = validated_data.pop("order_items")
        discount_code = validated_data.pop("discount_code", None)
        total_amount = 0
        for item_data in order_items_data:
            total_amount += item_data["quantity"] * item_data["menu_item"].get_discounted_price()

        # Endirim kodu tətbiqi
        discount_percentage = 0
        if discount_code:
            discount = DiscountCode.objects.filter(
                code=discount_code, is_deleted=False, is_used=False
            ).first()
            if not discount:
                raise serializers.ValidationError("Endirim kodu yanlışdır və ya istifadə olunub.")
            if discount.user != validated_data.get("user"):
                raise serializers.ValidationError("Bu endirim kodu sizin üçün deyil.")
            if discount.notification and discount.notification.title == "İlk Sifarişə 70% Endirim":
                if Order.objects.filter(user=validated_data.get("user"), is_deleted=False).exists():
                    raise serializers.ValidationError(
                        "70% endirim kodu yalnız ilk sifariş üçün keçərlidir."
                    )
                discount_percentage = 70.00
            elif discount.notification and discount.notification.title == "50 AZN Sifariş Endirimi":
                discount_percentage = 20.00
            else:
                discount_percentage = 20.00
            total_amount *= (1 - discount_percentage / 100)
            discount.is_used = True
            discount.save()
            logger.info(
                f"{discount_percentage}% endirim tətbiq olundu: "
                f"müştəri: {discount.user.email}, kod: {discount.code}, "
                f"yeni məbləğ: {total_amount} AZN"
            )

        validated_data["total_amount"] = total_amount
        order = Order.objects.create(**validated_data)

        for item_data in order_items_data:
            OrderItem.objects.create(
                order=order,
                menu_item=item_data["menu_item"],
                quantity=item_data["quantity"],
                price=item_data["menu_item"].get_discounted_price(),
            )

        # Bonus xalları
        bonus_points = 0
        if total_amount >= 50:
            bonus_points = 5
            BonusTransaction.objects.create(
                user=order.user,
                points=bonus_points,
                description="50 AZN sifarişdən qazanılan bonus",
                order=order
            )
            bonus_obj, created = BonusPoints.objects.get_or_create(
                user=order.user,
                defaults={"points": bonus_points}
            )
            if not created:
                bonus_obj.points += bonus_points
                bonus_obj.save()
            logger.info(
                f"Bonus qazanıldı: ID {order.id}, "
                f"müştəri: {order.user.email}, xallar: {bonus_points}"
            )

        # 50 AZN endirim kodu
        if total_amount >= 50:
            discount_code = str(uuid.uuid4())[:8]
            notification = Notification.objects.create(
                user=order.user,
                title="50 AZN Sifariş Endirimi",
                message=(
                    f"Hörmətli {order.user.email},\n\n"
                    f"50 AZN və ya daha çox sifariş etdiyiniz üçün 20% endirim kodu qazandınız!\n"
                    f"Kod: {discount_code}\n"
                    f"Növbəti sifarişinizdə istifadə edə bilərsiniz."
                ),
                sent_at=timezone.now()
            )
            DiscountCode.objects.create(
                user=order.user,
                code=discount_code,
                notification=notification
            )
            send_email_task.delay(
                subject="50 AZN Sifarişinizə Görə Endirim Kodu!",
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.user.email]
            )
            logger.info(
                f"50 AZN endirim kodu göndərildi: müştəri: {order.user.email}, kod: {discount_code}"
            )

        logger.info(
            f"Sifariş yaradıldı: ID {order.id}, "
            f"müştəri: {order.user.email}, məbləğ: {order.total_amount} AZN"
        )
        return order
        

class SalesReportSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    payment_type = serializers.ChoiceField(choices=PAYMENT_TYPE_CHOICES, required=False)
    orders = OrderSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    order_count = serializers.IntegerField(read_only=True)
    total_bonus_points = serializers.IntegerField(read_only=True)

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("bawlangic tariwi bitiw tarixinnen boyuk ola bilmez")
        return data

    
