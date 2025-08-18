from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
import random

from user.models import RefreshLog
from .models import Quest, RandomQuest, Stamp
from .serializers import QuestSerializer, RandomQuestSerializer, StampSerializer


# 퀘스트 목록 조회 + 생성
class QuestListCreateView(generics.ListCreateAPIView):
    queryset = Quest.objects.select_related("place").all()
    serializer_class = QuestSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# 오늘의 퀘스트 (랜덤 3개 제공)
class DailyQuestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()

        # 오늘 ACCEPTED 된 퀘스트 유지
        accepted_rqs = list(RandomQuest.objects.filter(
            user=user,
            created_at__date=today,
            status=RandomQuest.Status.ACCEPTED
        ))

        # 오늘 RANDOM_LIST 중 CLEAR/EXPIRED 제외, 3개 한도
        random_rqs = list(RandomQuest.objects.filter(
            user=user,
            created_at__date=today,
            status=RandomQuest.Status.RANDOM_LIST
        )[: (3 - len(accepted_rqs))])

        all_rqs = accepted_rqs + random_rqs

        # 부족하면 새로 채우기
        if len(all_rqs) < 3:
            excluded_ids = RandomQuest.objects.filter(
                user=user,
                created_at__date=today,
                status__in=[RandomQuest.Status.CLEAR, RandomQuest.Status.EXPIRED]
            ).values_list("quest_id", flat=True)

            accepted_ids = RandomQuest.objects.filter(
                user=user,
                status=RandomQuest.Status.ACCEPTED
            ).values_list("quest_id", flat=True)

            available = Quest.objects.exclude(id__in=excluded_ids).exclude(id__in=accepted_ids)
            if available.exists():
                need_count = 3 - len(all_rqs)
                sample = random.sample(list(available), min(need_count, available.count()))

                for quest in sample:
                    rq, _ = RandomQuest.objects.get_or_create(
                        user=user,
                        quest=quest,
                        defaults={"status": RandomQuest.Status.RANDOM_LIST},
                    )
                    all_rqs.append(rq)

        return Response(RandomQuestSerializer(all_rqs, many=True).data)


class RefreshRandomQuestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        today = timezone.now().date()

        # 오늘 새로고침 기록 확인
        if RefreshLog.objects.filter(user=user, refreshed_at__date=today).exists():
            return Response({"detail": "오늘은 이미 새로고침을 했습니다."}, status=400)

        # 새로고침 실행 → 기록 추가
        RefreshLog.objects.create(user=user)

        # 기존 RANDOM_LIST 만료 처리
        RandomQuest.objects.filter(
            user=user,
            status=RandomQuest.Status.RANDOM_LIST
        ).update(status=RandomQuest.Status.EXPIRED, updated_at=timezone.now())

        # 오늘 CLEAR / EXPIRED / ACCEPTED 된 퀘스트만 제외
        excluded_ids = RandomQuest.objects.filter(
            user=user,
            created_at__date=today,

            status__in=[RandomQuest.Status.CLEAR, RandomQuest.Status.EXPIRED, RandomQuest.Status.ACCEPTED]
        ).values_list("quest_id", flat=True)

        available = Quest.objects.exclude(id__in=excluded_ids)
        if not available.exists():
            return Response({"detail": "새로운 퀘스트를 불러올 수 없습니다."}, status=404)

        sample = random.sample(list(available), min(3, available.count()))
        new_rqs = []
        # update_or_create 로 중복 방지
        for quest in sample:
            rq, _ = RandomQuest.objects.update_or_create(
                user=user,
                quest=quest,
                defaults={
                    "status": RandomQuest.Status.RANDOM_LIST,
                    "updated_at": timezone.now(),
                },
            )
            new_rqs.append(rq)

        return Response(
            {
                "detail": "랜덤 퀘스트가 새로고침되었습니다.",
                "data": RandomQuestSerializer(new_rqs, many=True).data
            },
            status=status.HTTP_200_OK
        )


# 하루 리셋 (EXPIRED → RANDOM_LIST + 새로고침 기회 리셋)
class DayResetView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        # 1) EXPIRED → RANDOM_LIST 복구
        expired_updated = RandomQuest.objects.filter(
            user=user,
            status=RandomQuest.Status.EXPIRED
        ).update(status=RandomQuest.Status.RANDOM_LIST, updated_at=timezone.now())

        # 2) 새로고침 제한 리셋 → 오늘 기록 삭제
        deleted_logs = RefreshLog.objects.filter(user=user).delete()[0]

        return Response(
            {
                "detail": "하루가 리셋되었습니다.",
                "expired_reset": expired_updated,
                "refresh_reset": deleted_logs
            },
            status=status.HTTP_200_OK
        )



# 퀘스트 수락 / 완료
class QuestActionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk: int):
        user = request.user
        action = (request.data.get("action") or "").lower()

        quest = get_object_or_404(Quest, id=pk)

        rq, _ = RandomQuest.objects.get_or_create(
            user=user, quest=quest,
            defaults={"status": RandomQuest.Status.RANDOM_LIST},
        )

        if action == "accept":
            if rq.status == RandomQuest.Status.RANDOM_LIST:
                try:
                    rq.accept()
                except ValueError as e:
                    return Response({"detail": str(e)}, status=400)
                return Response(
                    {
                        "detail": "퀘스트를 수락했습니다.",
                        "data": RandomQuestSerializer(rq).data,
                    },
                    status=status.HTTP_200_OK
                )
            return Response({"detail": "이미 수락되었거나 만료/완료된 퀘스트입니다."}, status=400)

        elif action in ("complete", "clear"):
            if rq.status == RandomQuest.Status.ACCEPTED:
                try:
                    result = rq.clear()
                except ValueError as e:
                    return Response({"detail": str(e)}, status=400)
                return Response(
                    {
                        "detail": "퀘스트가 완료되었습니다.",
                        "data": RandomQuestSerializer(rq).data,
                        "extra": result,
                    },
                    status=status.HTTP_200_OK
                )
            return Response({"detail": "진행 중(ACCEPTED)인 퀘스트가 아닙니다."}, status=400)

        return Response({"detail": "action은 'accept' 또는 'complete'이어야 합니다."}, status=400)


# 나의 도감 조회
class StampListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StampSerializer

    def get_queryset(self):
        return Stamp.objects.filter(user=self.request.user).select_related("quest", "quest__place")
