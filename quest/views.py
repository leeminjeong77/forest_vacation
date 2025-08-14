from django.db import transaction
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Quest, RandomQuest, AcceptedQuest
from .serializers import QuestSerializer, AcceptedQuestSerializer, AcceptedQuestVerifySerializer


# 퀘스트 생성
class QuestCreateView(generics.CreateAPIView):
    queryset = Quest.objects.all()
    serializer_class = QuestSerializer

# 퀘스트 수락/완료
# body: {"action": "accept"} / {"action": "complete"}
class QuestActionView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        user = request.user
        action = (request.data.get("action") or "").lower()

        # 존재하는 퀘스트인지 확인
        quest = get_object_or_404(Quest, id=pk)

        random_quest, _ = RandomQuest.objects.get_or_create(
            user=user, quest=quest,
            defaults={"is_valid": True}
        )

        if action == "accept":
            # 진행 중(미완료) AcceptedQuest가 있으면 중복 수락 방지
            exists = AcceptedQuest.objects.filter(
                random_quest=random_quest, is_verified=False
            ).exists()
            if exists:
                return Response(
                    {"detail": "이미 수락한 퀘스트입니다."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            accepted = AcceptedQuest.objects.create(
                random_quest=random_quest,
                is_verified=False
            )
            return Response(
                {"detail": "퀘스트를 수락했습니다.", 
                 "data": AcceptedQuestSerializer(accepted).data},
                status=status.HTTP_201_CREATED
            )

        elif action == "complete":
            # 해당 유저의 진행중인 퀘스트
            accepted = AcceptedQuest.objects.filter(
                random_quest=random_quest, is_verified=False
            ).first()
            if not accepted:
                return Response(
                    {"detail": "진행중인 퀘스트가 없습니다."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 완료 처리
            serializer = AcceptedQuestVerifySerializer(
                accepted, data={"is_verified": True}, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                {"detail": "퀘스트가 완료되었습니다.", "data": serializer.data},
                status=status.HTTP_200_OK
            )

        else:
            return Response(
                {"detail": "action 값이 올바르지 않습니다. ('accept' 또는 'complete')"},
                status=status.HTTP_400_BAD_REQUEST
            )
