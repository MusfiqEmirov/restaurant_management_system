from rest_framework import serializers

from project_apps.core.constants import ROLE_CHOICES
from .models import *
from project_apps.core.logging import get_logger

logger = get_logger(__name__)

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
    
    def validate_email(self, value):
        if not value.strip():
            raise serializers.ValidationError("Invalid email address")
        return value


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_deleted=False),  # Only active users are included
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
        # Read-only fields that cannot be modified
        read_only_fields = [ 
            "id",
            "bonus_points",
            "created_at",
            "updated_at",
            "is_deleted"
        ]


class RegisterSerializer(UserSerializer):
    password = serializers.CharField(write_only=True, required=True)
    address = serializers.CharField(required=False, allow_blank=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['password', 'address']

    def create(self, validated_data):
        address = validated_data.pop('address', '')
        
        # Create User
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            role='customer'  # Default role is customer
        )
        
        # Create Profile
        Profile.objects.create(
            user=user,
            address=address
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        logger.debug(f"Login attempt: email={email}")

        if not email or not password:
            logger.error("Email or password not provided")
            raise serializers.ValidationError('Email and password are required')

        user = User.objects.filter(email=email, is_deleted=False, is_active=True).first()
        if not user:
            logger.error(f"User not found: email={email}, is_deleted=False, is_active=True")
            raise serializers.ValidationError('Account not found or is inactive')
        if not user.check_password(password):
            logger.error(f"Incorrect password: email={email}")
            raise serializers.ValidationError('Incorrect password')

        logger.info(f"User authentication successful: email={email}")
        data['user'] = user
        return data


class AdminUserCreateSerializer(serializers.ModelSerializer):
    # Only admins can create customers and staff users
    password = serializers.CharField(write_only=True, required=True)
    address = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'phone_number',
            'role',
            'password',
            'address',
            'created_at',
            'updated_at',
            'is_deleted'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def validate_role(self, value):
        valid_roles = ['customer', 'staff', 'admin']
        if value not in valid_roles:
            raise serializers.ValidationError('Role must be either customer, staff, or admin')
        return value

    def validate_email(self, value):
        if not value.strip():
            raise serializers.ValidationError('Invalid email')
        if User.objects.filter(email=value, is_deleted=False).exists():
            raise serializers.ValidationError('This email is already taken')
        return value

    def create(self, validated_data):
        address = validated_data.pop('address', '')
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            role=validated_data['role']
        )
        from project_apps.accounts.models import Profile
        Profile.objects.create(
            user=user,
            address=address
        )
        return user
