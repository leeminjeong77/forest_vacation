from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Quest, RandomQuest, Stamp
from .serializers import QuestSerializer, RandomQuestSerializer, StampSerializer

# 퀘스트 목록 + 생성
class QuestListCreateView(generics.ListCreateAPIView):
    queryset = Quest.objects.select_related("place").all()
    serializer_class = QuestSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# 수락/완료
class QuestActionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk: int):
        user = request.user
        action = (request.data.get("action") or "").lower()

        quest = get_object_or_404(Quest, id=pk)

        # 유저-퀘스트 슬롯 가져오거나 생성
        rq, _ = RandomQuest.objects.get_or_create(
            user=user, quest=quest,
            defaults={"status": RandomQuest.Status.RANDOM_LIST},
        )

        if action == "accept":
            # RANDOM_LIST 에서만 수락 허용
            if rq.status == RandomQuest.Status.RANDOM_LIST:
                try:
                    rq.accept()  # status -> ACCEPTED
                except ValueError as e:
                    return Response({"detail": str(e)}, status=400)
                return Response(
                    {"detail": "퀘스트를 수락했습니다.", "data": RandomQuestSerializer(rq).data},
                    status=status.HTTP_200_OK
                )
            return Response({"detail": "이미 수락되었거나 만료/완료된 퀘스트입니다."}, status=400)

        elif action in ("complete", "clear"):
            # ACCEPTED 상태에서만 완료 가능
            if rq.status == RandomQuest.Status.ACCEPTED:
                try:
                    rq.clear()  # status -> CLEAR, 내부에서 Stamp.get_or_create(...)
                except ValueError as e:
                    return Response({"detail": str(e)}, status=400)
                return Response(
                    {"detail": "퀘스트가 완료되었습니다.", "data": RandomQuestSerializer(rq).data},
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
