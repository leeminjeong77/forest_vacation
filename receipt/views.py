import json
import uuid
import time
import requests
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import Receipt
from .serializers import ReceiptCreateSerializer, ReceiptSerializer
from quest.models import RandomQuest


class ReceiptUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ReceiptCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        receipt = serializer.save(user=request.user)

        # OCR API 요청
        payload = {
            "version": "V2",
            "requestId": str(uuid.uuid4()),
            "timestamp": int(time.time() * 1000),
            "images": [{"format": "jpg", "name": "receipt"}],
        }

        files = {
            "file": receipt.image.open("rb"),
            "message": (None, json.dumps(payload), "application/json"),
        }

        headers = {"X-OCR-SECRET": settings.CLOVA_OCR_SECRET_KEY}
        response = requests.post(
            settings.CLOVA_OCR_INVOKE_URL, headers=headers, files=files
        )

        extra = None

        if response.status_code == 200:
            data = response.json()

            receipt.ocr_uid = data.get("images", [{}])[0].get("uid")
            receipt.status = Receipt.Status.SUCCESS
            receipt.message = "인식 성공"

            store_name = (
                data.get("images", [{}])[0]
                .get("receipt", {})
                .get("result", {})
                .get("storeInfo", {})
                .get("name", {})
                .get("text")
            )
            total_price = (
                data.get("images", [{}])[0]
                .get("receipt", {})
                .get("result", {})
                .get("totalPrice", {})
                .get("price", {})
                .get("formatted")
            )

            receipt.store_name = store_name
            receipt.total_price = int(total_price) if total_price else None
            receipt.save()

            # 퀘스트 완료 처리
            rq = RandomQuest.objects.filter(
                user=request.user, quest=receipt.quest
            ).first()

            if rq:
                handlers = {
                    RandomQuest.Status.ACCEPTED: self._handle_accepted,
                    RandomQuest.Status.CLEAR: self._handle_clear,
                    RandomQuest.Status.RANDOM_LIST: self._handle_invalid,
                    RandomQuest.Status.EXPIRED: self._handle_invalid,
                }
                handler = handlers.get(rq.status, self._handle_not_found)
                extra = handler(receipt, rq)
            else:
                receipt.status = Receipt.Status.FAILURE
                receipt.message = "해당 퀘스트를 찾을 수 없습니다."
                receipt.save()

        else:
            receipt.status = Receipt.Status.FAILURE
            receipt.message = f"OCR 실패 ({response.status_code})"
            receipt.save()

        response_data = ReceiptSerializer(receipt).data
        if extra:
            response_data["extra"] = extra

        return Response(response_data, status=status.HTTP_201_CREATED)

    # --- 상태별 핸들러 메서드들 ---

    def _handle_accepted(self, receipt, rq):
        """수락된 퀘스트 → OCR 결과와 place 이름 비교"""
        if (
            receipt.store_name
            and receipt.quest.place.name
            and receipt.store_name.strip() == receipt.quest.place.name.strip()
        ):
            try:
                receipt.status = Receipt.Status.SUCCESS
                receipt.message = "영수증 인증 성공"
                extra = rq.clear()
            except ValueError as e:
                receipt.status = Receipt.Status.FAILURE
                receipt.message = f"퀘스트 완료 처리 실패: {str(e)}"
                extra = {"detail": receipt.message}
        else:
            receipt.status = Receipt.Status.FAILURE
            receipt.message = "가게명이 일치하지 않습니다."
            extra = {"detail": receipt.message}

        receipt.save()
        return extra

    def _handle_clear(self, receipt, rq):
        """이미 완료된 퀘스트"""
        receipt.status = Receipt.Status.FAILURE
        receipt.message = "이미 완료된 퀘스트입니다."
        receipt.save()
        return {"detail": receipt.message}

    def _handle_invalid(self, receipt, rq):
        """수락되지 않은 상태 (랜덤 노출 or 만료)"""
        receipt.status = Receipt.Status.FAILURE
        receipt.message = "수락되지 않은 퀘스트입니다."
        receipt.save()
        return {"detail": receipt.message}

    def _handle_not_found(self, receipt, rq):
        """퀘스트 자체를 찾을 수 없을 때"""
