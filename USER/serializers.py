from rest_framework import serializers
from . import models
import re
from rest_framework.authentication import authenticate
from rest_framework.authtoken.models import Token




class SignUpSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField()
    password = serializers.CharField(write_only=True, required=True)
    confirmation_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = models.CustomUser
        fields = ["id", "username", "first_name", "last_name", "phone_number", "password", "confirmation_password"]

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("confirmation_password"):
            raise serializers.ValidationError(
                    detail={
                        "confirmation_password":"Parol va tasdiqlash paroli bir xil emas!"
                    }
            )
            
        return attrs
    
        
    def validate_username(self, username):
        if username[0].isdigit():
            raise serializers.ValidationError(
                    detail={
                        "username":"Username raqam bilan boshlanmasligi zarur!"
                    }
            )
        
        return username


    def validate_first_name(self, first_name):
        if not first_name.isalpha():
            raise serializers.ValidationError(
                    detail={
                        "first_name":"Ism to'liq harflardan iborat bo'lishi kerak!"
                    }
            )

        return first_name


    def validate_last_name(self, last_name):
        if not last_name.isalpha():
            raise serializers.ValidationError(
                detail={
                        "last_name":"Familiya to'liq harflardan iborat bo'lishi kerak!"
                }
            )

        return last_name
          
          
    def validate_phone_number(self, phone_number):

        pattern = r'^\+998\d{9}$'

        if not re.match(pattern=pattern, string=phone_number):
            raise serializers.ValidationError(
                detail={
                    "phone_number":"Telefon raqami noto'g'ri formatda kiritildi. Masalan: +998901234567"
                }
            )

        if models.CustomUser.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError(
                detail={
                    "phone_number":"Bu raqam bilan avval ro'yxatdan o'tishgan!"
                }
            )
        
        return phone_number


    def validate_password(self, password):
        if len(password)<6:
            raise serializers.ValidationError(
                detail={
                    "password":"Parol kamida 6 ta belgidan iborat bo'lishi kerak!",
                }
            )

        return password


    def create(self, validated_data):
        validated_data.pop("confirmation_password")
        user = models.CustomUser.objects.create_user(**validated_data)
        return user


    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            "message":"Ro'yxatdan muvaffaqiyatli o'tdingiz🎉",
            "user":data
        }
    

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs.get("username"), password=attrs.get("password"))

        if user is None:
            raise serializers.ValidationError("Username yoki password noto'g'ri!")

        attrs["user"]=user

        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    # id = serializers.ReadOnlyField()
    class Meta:
        model = models.CustomUser
        fields = ["id", "username", "first_name", "last_name", "phone_number"]

    
class ProfileUpdateSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    class Meta:
        model = models.CustomUser
        fields = ["id", "username", "first_name", "last_name", "phone_number"]

    def validate_phone_number(self, phone_number):
        pattern = r"^\+998\d{9}$"
        if phone_number and not re.match(pattern=pattern, string=phone_number):
            raise serializers.ValidationError(
                "Telefon raqami noto'g'ri formatda kiritildi. Masalan: +998901234567"
            )
        return phone_number
    

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirmation_password = serializers.CharField(write_only=True)


    def validate(self, attrs):
        if not attrs.get("new_password"):
            raise serializers.ValidationError(
                detail={
                    "message":"Yangi parol bo'sh bo'lmasligi lozim!"
                }
            )

        if attrs.get("new_password") != attrs.get("confirmation_password"):
            raise serializers.ValidationError(
                detail={
                    "message":"Yangi parol va tasdiqlash paroli bir xil bo'lishi lozim!"
                }
            )

        if attrs.get("old_password") == attrs.get("new_password"):
            raise serializers.ValidationError(
                detail={
                    "message":"Eski parol va yango parol bir xil bo'lmasligi lozim!"
                }
            )
        
        return attrs


    def validate_old_password(self, old_password):
        user = self.context.get("request").user

        if not user.check_password(old_password):
            raise serializers.ValidationError(
                detail={
                    "message":"Eski parol xato!"
                }
            )

        return old_password


    def validate_new_password(self, new_password):
        if len(new_password)<6:
            raise serializers.ValidationError(
                detail={
                    "new_password":"Parol kamida 6 ta belgidan iborat bo'lishi kerak!",
                }
            )

        return new_password


    def save(self, **kwargs):
        user = self.context.get("request").user
        user.set_password(self.validated_data.get("new_password"))
        user.save()
        return user


    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {"message":"Password changed successfully✅"}


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = models.Post
        fields = ["id", "title", "content", "author", "created_at", "updated_at"]