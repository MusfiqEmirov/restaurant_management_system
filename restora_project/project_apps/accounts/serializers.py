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
    user = UserSerializer(read_only=True)
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


class RegisterSerializer(UserSerializer):
    password = serializers.CharField(write_only=True, required=True)
    address = serializers.CharField(required=False, allow_blank=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['password', 'address']

    def create(self, validated_data):
        address = validated_data.pop('address', '')
        
        # User yaradırıq
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            role='customer'  # Avtomatik musteri rolu
        )
        
        # Profile yaradırıq
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

        logger.debug(f"Login cəhdi: email={email}")

        if not email or not password:
            logger.error("email ve ya parol daxil edilmeyib")
            raise serializers.ValidationError('email ve [parol teleb olunur]')

        user = User.objects.filter(email=email, is_deleted=False, is_active=True).first()
        if not user:
            logger.error(f"User tapılmadı: email={email}, is_deleted=False, is_active=True")
            raise serializers.ValidationError('hesab tapilmadi ve ya aktiv deyil')
        if not user.check_password(password):
            logger.error(f"Parol yalniwdir: email={email}")
            raise serializers.ValidationError('parol yalniwdir')

        logger.info(f"user dogrulama ugurla bas tutdu email={email}")
        data['user'] = user
        return data
    

class AdminUserCreateSerializer(serializers.ModelSerializer):
    # sadece admin musteri ve user(isci yarada biler)
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
            raise serializers.ValidationError('yalniz musteri staff ve ya admin role sece biler')
        return value

    def validate_email(self, value):
        if not value.strip():
            raise serializers.ValidationError('email yalniwdir')
        if User.objects.filter(email=value, is_deleted=False).exists():
            raise serializers.ValidationError('artiq bu email movcuddur')
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