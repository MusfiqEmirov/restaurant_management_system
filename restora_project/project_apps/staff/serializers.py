from rest_framework import serializers

from .models import Staff
from project_apps.accounts.serializers import UserSerializer
from project_apps.accounts.models import User
from project_apps.core.constants import ROLE_CHOICES


class StaffSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_deleted=False),
        source="user",
        write_only=True
    )

    class Meta:
        model = Staff
        fields = [
            "id",
            "user",
            "user_id",
            "role",
            "is_active",
            "created_at",
            "updated_at",
            "is_deleted"
        ]
        # Read-only fields that cannot be modified
        read_only_fields = [ 
            "id",
            "created_at",
            "updated_at",
            "is_deleted"
        ]
    
    def validate_role(self, value):
        valid_roles = [choice[0] for choice in ROLE_CHOICES]
        if value not in valid_roles:
            raise serializers.ValidationError("Invalid role selected")
        return value
