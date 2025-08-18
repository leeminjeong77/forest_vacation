from rest_framework import serializers
from .models import PointTransaction

# 퀘스트 완료 인증 시 (포인트는 서버에서 처리)
class QuestCompleteSerializer(serializers.Serializer):
    quest_name = serializers.CharField(max_length=100)


# 교환권 사용 요청 시
class VoucherUseSerializer(serializers.Serializer):
    voucher_name = serializers.CharField(max_length=100)

class PointTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointTransaction
        fields = ['id', 'amount', 'reason', 'created_at']