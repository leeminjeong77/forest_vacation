from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import ItemExchange
from .serializers import ItemExchangeSerializer, ItemExchangeCreateSerializer
from reward.models import Reward
from point.models import PointTransaction
from django.db.models import Sum
from django.utils import timezone

# Create your views here.

# 모든 아이템(보상) 목록 조회 API
@api_view(['GET'])
@permission_classes([AllowAny])
def all_items(request):
    """GET /items/all/ - 모든 보상 목록 조회"""
    rewards = Reward.objects.all().order_by('id')
    
    # 응답 형식에 맞게 데이터 구성
    items_data = []
    for reward in rewards:
        items_data.append({
            "id": reward.id,
            "name": reward.name,
            "price": reward.price,
            "weight": reward.weight
        })
    
    return Response(items_data, status=status.HTTP_200_OK)

# 아이템 교환 API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def exchange_item(request):
    """POST /items/exchange/ - 포인트로 아이템 교환"""
    user = request.user
    serializer = ItemExchangeCreateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    reward_id = serializer.validated_data['reward']
    try:
        reward = Reward.objects.get(id=reward_id)
    except Reward.DoesNotExist:
        return Response({"error": "해당 보상이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
    
    # 사용자 현재 포인트 확인
    current_points = user.point_transactions.aggregate(total=Sum('amount'))['total'] or 0
    
    if current_points < reward.price:
        return Response({"error": "포인트가 부족합니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    # 이미 교환한 아이템인지 확인
    if ItemExchange.objects.filter(user=user, reward=reward).exists():
        return Response({"error": "이미 교환한 아이템입니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    # 포인트 차감
    PointTransaction.objects.create(
        user=user,
        amount=-reward.price,
        reason=f"아이템 교환: {reward.name}"
    )
    
    # ItemExchange 생성
    item_exchange = ItemExchange.objects.create(
        user=user,
        reward=reward
    )
    
    return Response({
        "message": f"{reward.name}을(를) 교환했습니다.",
        "item_id": item_exchange.id,
        "points_deducted": reward.price
    }, status=status.HTTP_201_CREATED)

# 사용자 보유 아이템 목록 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_items(request):
    """GET /items/my/ - 사용자 보유 아이템 목록"""
    user_items = ItemExchange.objects.filter(user=request.user).order_by('-exchanged_at')
    serializer = ItemExchangeSerializer(user_items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# 아이템 사용 API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def use_item(request, pk):
    """POST /items/{pk}/use/ - 아이템 사용"""
    try:
        item = ItemExchange.objects.get(id=pk, user=request.user)
    except ItemExchange.DoesNotExist:
        return Response({"error": "해당 아이템이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
    
    if item.is_used:
        return Response({"error": "이미 사용된 아이템입니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    item.is_used = True
    item.used_at = timezone.now()
    item.save()
    
    return Response({
        "message": f"{item.reward.name}을(를) 사용했습니다.",
        "item_id": item.id
    }, status=status.HTTP_200_OK)
