from rest_framework import serializers

from .models import *
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