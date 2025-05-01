from rest_framework import serializers

from .models import Notification, DiscountCode, BonusPoints, AdminCode
from project_apps.accounts.serializers import UserSerializer
from project_apps.accounts.models import User


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
    
    def validate_sent_at(self, value):
        if value is None and self.instance is None:
            raise serializers.ValidationError("gonderilme tarixi qeyd edilmeldiir ")
        return value


class DiscountCodeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_deleted=False, role='customer'),
        source="user",
        write_only=True
    )
    notification = NotificationSerializer(read_only=True)

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
    
    
class BonusPointsSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_deleted=False, role='customer'),
        source="user",
        write_only=True
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