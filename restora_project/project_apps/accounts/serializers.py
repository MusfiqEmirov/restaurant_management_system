from rest_framework import serializers

from project_apps.core.constants import ROLE_CHOICES
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "role",
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

        def validate_role(self, value):
            valid_roles = [choice[0] for choice in ROLE_CHOICES]
            if value not in valid_roles:
                raise serializers.ValidationError("yalnis rol deyeri secildi")
            return value
        
        def validate_email(self, value):
            if not value.strip():
                raise serializers.ValidationError("e-poct unvani ve ya mailiniz yalnisdir")
            return value
        

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializers(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_deleted=False), # yalniz silinmemiw istifadeciler alinir
        source="user",
        write_only=True
    )

    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "user_id",
            "bonus_points",
            "created_at",
            "updated_at",
            "is_deleted",
            "address",
        ]
         # ancaq oxuna biler deyiwdirile bilmez
        read_only_fields = [ 
            "id",
            "bonus_points",
            "created_at",
            "updated_at",
            "is_deleted"
        ]
