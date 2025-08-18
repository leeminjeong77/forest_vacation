from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserReward
from .serializers import UserRewardSerializer

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