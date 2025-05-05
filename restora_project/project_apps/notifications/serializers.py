from rest_framework import serializers

from .models import (Notification,
                     DiscountCode,
                     BonusPoints,
                     AdminCode,
                     Message,
                     
                     )
from project_apps.accounts.serializers import UserSerializer
from project_apps.accounts.models import User
from project_apps.orders.models import Order, OrderItem
from project_apps.orders.serializers import OrderItemSerializer,OrderSerializer


class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_deleted=False),
        source="user",
        write_only=True
    )

    class Meta:
        model = Notification
        fields = [
            "id",
            "user",
            "user_id",
            "title",
            "message",
            "is_read",
            "sent_at",
            "created_at",
            "updated_at",
            "is_deleted"
        ]
         # ancaq oxuna biler deyiwdirile bilmez
        read_only_fields = [ 
            "id",
            "created_at",
            "updated_at",
            "is_deleted"
        ]

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("basliq bow olmamalidir")
        return value

    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("mesaj bow ola bilmez")
        return value
    

class DiscountCodeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_deleted=False, role='customer'),
        source="user",
        write_only=True
    )
    notification = NotificationSerializer(read_only=True)
    notification_id = serializers.PrimaryKeyRelatedField(
        queryset=Notification.objects.filter(is_deleted=False),
        source="notification",
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = DiscountCode
        fields = [
            "id",
            "user",
            "user_id",
            "code",
            "is_used",
            "notification",
            "created_at",
            "updated_at",
            "is_deleted"
        ]
        read_only_fields = [
            "id",
            "code",
            "created_at",
            "updated_at",
            "is_deleted"
        ]

    def validate_code(self, value):
        if not value:
            raise serializers.ValidationError("Kod bos ola bilmez")
        return value

    def validate_is_used(self, value):
        if self.instance and self.instance.is_used and not value:
            raise serializers.ValidationError("bu kod bir defe istifade olunub tekrar istifad eeleemk olmaz")
        return value
    
    def validate(self, data):
        user = data.get("user")
        notification = data.get("notification")
        if notification and notification.title == "İlk Sifarişə 70% Endirim":
            if Order.objects.filter(user=user, is_deleted=False).exists():
                raise serializers.ValidationError(
                    "70% endirim kodu yalnız ilk sifariş üçün keçərlidir."
                )
        return data
    
    
class BonusPointsSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_deleted=False, role='customer'),
        source="user",
        write_only=True
    )
    order = OrderSerializer(read_only=True)
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.filter(is_deleted=False),
        source="order",
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = BonusPoints
        fields = [
            "id",
            "user",
            "user_id",
            "points",
            "last_notified_points",
            "created_at",
            "updated_at",
            "is_deleted"
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "is_deleted"
        ]

    def validate_points(self, value):
        if value < 0:
            raise serializers.ValidationError("Xallar menfi ola bilmez")
        return value

    def validate_last_notified_points(self, value):
        if value < 0:
            raise serializers.ValidationError("Son bildiriw xallar menfi ola bilmez")
        return value    


class AdminCodeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_deleted=False, is_staff=True),
        source="user",
        write_only=True
    )
    notification = NotificationSerializer(read_only=True)

    class Meta:
        model = AdminCode
        fields = [
            "id",
            "user",
            "user_id",
            "code",
            "notification",
            "created_at",
            "updated_at",
            "is_deleted"
        ]
        read_only_fields = [
            "id",
            "code",
            "created_at",
            "updated_at",
            "is_deleted"
        ]

    def validate_code(self, value):
        if not value:
            raise serializers.ValidationError("Kod bow ola bilmez")
        return value
    

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_deleted=False),
        default=serializers.CurrentUserDefault()
    )
    recipient = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_deleted=False)
    )

    class Meta:
        model = Message
        fields = ['id',
                  'sender',
                  'recipient',
                  'content',
                  'is_read',
                  'notification',
                  'created_at',
                  'updated_at'
                  ]
        read_only_fields = ['id',
                            'sender',
                            'is_read',
                            'notification',
                            'created_at',
                            'updated_at'
                            ]

    def validate(self, data):
        sender = self.context['request'].user
        recipient = data.get('recipient')
        if sender == recipient:
            raise serializers.ValidationError("ozune mesaj gondermek olmaz")
        if sender.role == 'customer' and recipient.role != 'admin':
            raise serializers.ValidationError("musteriler yalnis admine mesaj gondere biler")
        if sender.role == 'admin' and recipient.role != 'customer':
            raise serializers.ValidationError("adminler yalniz musterilere mesaj gondere biler")
        return data    