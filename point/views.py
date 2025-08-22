from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum
from .models import PointTransaction
from quest.models import RandomQuest
from receipt.models import Receipt
from reward.models import Reward, UserReward
from notification.models import Notification
from .serializers import QuestCompleteSerializer, VoucherUseSerializer, PointTransactionSerializer

# 퀘스트 완료 → 포인트 적립 + 알람
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quest_complete(request):
    serializer = QuestCompleteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = request.user
    quest_id = serializer.validated_data['quest_id']
    
    # -----------------------------
    # TODO: 영수증 인증 개발 완료 시 다시 활성화
    # 현재는 프론트 OCR 개발 대기 상태라 주석 처리
    #
    # verified = Receipt.objects.filter(
    #     user=user,
    #     quest_id=quest_id,
    #     status=Receipt.Status.SUCCESS
    # ).exists()
    # if not verified:
    #     return Response({"error": "영수증 인증이 완료되지 않았습니다."}, status=400)
    # -----------------------------
    
   # (2) 진행중 or 완료 상태 확인
    try:
        rq = RandomQuest.objects.get(
            user=user,
            quest_id=quest_id,
            status__in=[RandomQuest.Status.ACCEPTED, RandomQuest.Status.CLEAR]
        )
    except RandomQuest.DoesNotExist:
        return Response({"error": "진행 중인 퀘스트가 아닙니다."}, status=400)
    
    # (3) clear() 실행 (완료 퀘스트로 상태 변경 + 도감 생성)
    if rq.status != RandomQuest.Status.CLEAR:
        rq.clear()

    # 포인트 적립
    points = rq.quest.reward_points

    reason = f"퀘스트 완료: {quest_id}"
    transaction = PointTransaction.objects.create(
        user=user,
        amount=points,
        reason=reason
    )

    # 알람 생성
    try:
        Notification.objects.create(user=user, title="퀘스트 완료", content=f"{points}포인트가 적립되었습니다. ({reason})")
    except Exception as e:
        print(f"알람 생성 실패: {e}")

  
    return Response({
        "message": "포인트가 자동 적립되었습니다.",
        "transaction_id": transaction.id,
        "points_added": points,
        "reason": reason
    }, status=201)


# 교환권 구매 → 포인트 차감 + 알람 + UserReward 생성
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def voucher_use(request):
    user = request.user
    voucher_name = request.data.get('voucher_name')

    reward = Reward.objects.filter(name=voucher_name).first()
    if not reward:
        return Response({"error": "해당 교환권이 없습니다."}, status=404)


    # 포인트 차감
    reason = f"교환권 구매: {reward.name}"
    transaction = PointTransaction.objects.create(
        user=user,
        amount=-reward.price,
        reason=reason
    )

    # 알람 생성
    try:
        Notification.objects.create(
            user=user,
            title="포인트 차감",
            content=f"{reward.price}포인트가 차감되었습니다. ({reason})"
        )
    except Exception as e:
        print(f"알람 생성 실패: {e}")

    # UserReward 생성
    user_reward = UserReward.objects.create(user=user, reward=reward)

    return Response({
        "message": f"{reward.name} 교환권을 구매했습니다.",
        "points_deducted": reward.price,
        "transaction_id": transaction.id,
        "user_reward_id": user_reward.id
    }, status=201)


# 포인트 내역 전체 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def point_transaction_list(request):
    transactions = PointTransaction.objects.filter(user=request.user).order_by('-created_at')
    serializer = PointTransactionSerializer(transactions, many=True)
    return Response(serializer.data)