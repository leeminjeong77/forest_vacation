from rest_framework import serializers
from .models import Receipt

# 영수증 생성 (업로드)
class ReceiptCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = ["id", "quest", "image"]

# 영수증 조회
class ReceiptSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Receipt
        fields = [
            "id",
            "user",
            "store_name",
            "total_price",
            "status",
            "message",
            "image",
            "created_at",
            "updated_at",
        ]