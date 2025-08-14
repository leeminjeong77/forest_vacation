from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import PointTransaction
from reward.models import Reward, UserReward
from .serializers import QuestCompleteSerializer, VoucherUseSerializer, PointTransactionSerializer
from rest_framework.generics import ListAPIView
from django.db.models import Sum

# Create your views here.

class QuestCompleteView(generics.GenericAPIView):
    serializer_class = QuestCompleteSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        quest_name = serializer.validated_data['quest_name']

         # 포인트 정책 (퀘스트별)
        QUEST_POINT_MAP = {
            "영수증 인증 미션": 100,
        }
        points = QUEST_POINT_MAP.get(quest_name)

        if points is None:
            return Response({"error": "해당 퀘스트에 대한 포인트 정책이 없습니다."},
                            status=400)
        

        # 포인트 적립
        reason = f"퀘스트 완료: {quest_name}"
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
        user = request.user
        voucher_name = request.data.get('voucher_name')

        reward = Reward.objects.filter(name=voucher_name).first()
        if not reward:
            return Response({"error": "해당 교환권이 없습니다."},
                            status=404)

        current_points = user.point_transactions.aggregate(total=Sum('amount'))['total'] or 0
        if current_points < reward.price:
            return Response({"error": "포인트가 부족합니다."},
                            status=400)

        # 포인트 차감
        reason = f"교환권 구매: {reward.name}"
        transaction = PointTransaction.objects.create(
            user=user,
            amount=-reward.price,
            reason=reason
        )

        user_reward = UserReward.objects.create(user=user, reward=reward)
        return Response({
            "message": f"{reward.name} 교환권을 구매했습니다.",
            "points_deducted": reward.price,
            "transaction_id": transaction.id,
            "user_reward_id": user_reward.id
        }, status=201)
    
class PointTransactionListView(ListAPIView):
    serializer_class = PointTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PointTransaction.objects.filter(user=self.request.user).order_by('-created_at')