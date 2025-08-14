from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import PointTransaction
from .serializers import QuestCompleteSerializer, VoucherUseSerializer, PointTransactionSerializer
from rest_framework.generics import ListAPIView
from django.db.models import Sum

# Create your views here.

# 퀘스트별 포인트 정책
QUEST_POINT_MAP = {
    "영수증 인증 미션": 100,
}


VOUCHER_COST_MAP = {
    "뽑기 교환권": 300,
    "스페이스 교환권": 3000,
}

class QuestCompleteView(generics.GenericAPIView):
    serializer_class = QuestCompleteSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        quest_name = serializer.validated_data['quest_name']
        points = QUEST_POINT_MAP.get(quest_name)

        if points is None:
            return Response({"error": "해당 퀘스트에 대한 포인트 정책이 없습니다."},
                            status=400)
        

        # 포인트 적립
        transaction = PointTransaction.objects.create(
            user=user,
            amount=points,
            reason=f"퀘스트 완료: {quest_name}"
        )
        return Response({"message": "포인트가 자동 적립되었습니다.",
                         "transaction_id": transaction.id,
                         "points_added": points,
                         "reason": reason}, status=201)


class VoucherUseView(generics.GenericAPIView):
    serializer_class = VoucherUseSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        voucher_name = serializer.validated_data['voucher_name']
        cost = VOUCHER_COST_MAP.get(voucher_name)

        if cost is None:
            return Response({"error": "해당 교환권에 대한 비용 정책이 없습니다."},
                            status=400)

        current_points = user.point_transactions.aggregate(total=Sum('amount'))['total'] or 0
        if current_points < cost:
            return Response({"error": "포인트가 부족합니다."},
                            status=400)

        # 포인트 차감
        transaction = PointTransaction.objects.create(
            user=user,
            amount=-cost,
            reason=f"교환권 사용: {voucher_name}"
        )
        return Response({"message": "포인트가 자동 차감되었습니다.",
                         "transaction_id": transaction.id,
                         "points_deducted": cost,
                         "reason": reason}, status=status.HTTP_201_CREATED)
    
class PointTransactionListView(ListAPIView):
    serializer_class = PointTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PointTransaction.objects.filter(user=self.request.user).order_by('-created_at')