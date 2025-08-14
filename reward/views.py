from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import UserReward
from .serializers import UserRewardSerializer, RewardUseSerializer

# Create your views here.

# 사용자 보유 교환권 조회
class UserRewardListView(generics.ListAPIView):
    serializer_class = UserRewardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserReward.objects.filter(user=self.request.user, is_used=False).order_by('-created_at')

# UserReward 사용
class UserRewardUseView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        user_reward = UserReward.objects.get(id=pk, user=request.user)  # 존재하지 않으면 500 에러
        reward_name = user_reward.reward.name
        user_reward.delete()

        return Response({"message": f"{reward_name} 교환권을 사용했습니다."}, status=200)