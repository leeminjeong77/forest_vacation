from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from django.db import transaction
import random
from .models import UserReward, Reward
from .serializers import UserRewardSerializer, RewardSerializer, RewardCreateSerializer
from point.models import PointTransaction

# 보상 생성 API
@api_view(['POST'])
@permission_classes([AllowAny])  # 관리자만 접근하도록 설정 가능
def create_reward(request):
    serializer = RewardCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 보상 목록 조회 API
@api_view(['GET'])
@permission_classes([AllowAny])
def reward_list(request):
    rewards = Reward.objects.all().order_by('id')
    serializer = RewardSerializer(rewards, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# 보상 뽑기 API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def draw_reward(request):
    user = request.user
    
    # 사용자 현재 포인트 확인
    current_points = user.point_transactions.aggregate(total=Sum('amount'))['total'] or 0
    
    if current_points < 20:
        return Response({"error": "포인트가 부족합니다. 20포인트가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    # 모든 보상의 가중치 합계 계산
    total_weight = Reward.objects.aggregate(total=Sum('weight'))['total'] or 0
    
    if total_weight == 0:
        return Response({"error": "뽑을 수 있는 보상이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    # 가중치 기반 랜덤 선택
    random_value = random.randint(1, total_weight)
    cumulative_weight = 0
    selected_reward = None
    
    for reward in Reward.objects.all():
        cumulative_weight += reward.weight
        if random_value <= cumulative_weight:
            selected_reward = reward
            break
    
    if not selected_reward:
        return Response({"error": "보상 선택에 실패했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # 포인트 차감 (20포인트)
    PointTransaction.objects.create(
        user=user,
        amount=-20,
        reason=f"보상 뽑기: {selected_reward.name}"
    )
    
    # UserReward 생성
    user_reward = UserReward.objects.create(
        user=user,
        reward=selected_reward
    )
    
    return Response({
        "reward_id": selected_reward.id,
        "name": selected_reward.name,
        "message": f"{selected_reward.name}을(를) 획득했습니다!"
    }, status=status.HTTP_200_OK)


# 사용자 보유 교환권 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_reward_list(request):
    user_rewards = UserReward.objects.filter(user=request.user, is_used=False).order_by('-created_at')
    serializer = UserRewardSerializer(user_rewards, many=True)
    return Response(serializer.data)


# UserReward 사용 (삭제)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def use_user_reward(request, pk):
    try:
        user_reward = UserReward.objects.get(id=pk, user=request.user)
    except UserReward.DoesNotExist:
        return Response({"error": "사용할 수 없는 교환권입니다."}, status=404)

    reward_name = user_reward.reward.name
    user_reward.delete()

    return Response({"message": f"{reward_name} 교환권을 사용했습니다."}, status=200)