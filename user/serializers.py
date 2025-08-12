from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "student_num",
            "password",
            "gender",
            "department",
            "point",
            "profile_image",
            "nickname",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "student_num": {"required": True},
            "point": {"read_only": True},
        }


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "student_num",
            "gender",
            "department",
            "nickname",
            "point",
            "profile_image",
        ]