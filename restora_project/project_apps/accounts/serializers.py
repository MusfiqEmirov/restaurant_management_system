from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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
    

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        """
        email ve parol ile giriw
        """
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError('email ve parol teleb olunur')

        user = User.objects.filter(email=email, is_deleted=False).first()
        if not user or not user.check_password(password):
            raise serializers.ValidationError('email ve ya parol yalniwdir')

        if not user.is_active:
            raise serializers.ValidationError('bu hesab aktiv deyil')

        data = super().validate(attrs)
        data['user'] = {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'role': user.role
        }
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