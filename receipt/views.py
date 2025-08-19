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
        if serializer.is_valid():
            receipt = serializer.save(user=request.user)

            # OCR API 요청
            payload = {"version": "V2", "requestId": str(uuid.uuid4()), "timestamp": int(time.time() * 1000), "images": [{"format": "jpg", "name": "receipt"}]}

            files = {'file': receipt.image.open("rb"),'message': (None, json.dumps(payload), 'application/json')}

            headers = {"X-OCR-SECRET": settings.CLOVA_OCR_SECRET_KEY}
            response = requests.post(settings.CLOVA_OCR_INVOKE_URL,headers=headers,files=files)

            extra = None

            if response.status_code == 200:
                data = response.json()

                receipt.ocr_uid = data.get("images", [{}])[0].get("uid")
                receipt.status = Receipt.Status.SUCCESS
                receipt.message = "인식 성공"

                store_name = (data.get("images", [{}])[0].get("receipt", {}).get("result", {}).get("storeInfo", {}).get("name", {}).get("text"))
                total_price = (data.get("images", [{}])[0].get("receipt", {}).get("result", {}).get("totalPrice", {}).get("price", {}).get("formatted"))

                receipt.store_name = store_name
                receipt.total_price = int(total_price) if total_price else None
                receipt.save()

                # 퀘스트 완료 처리
                rq = RandomQuest.objects.filter(user=request.user, quest=receipt.quest).first()
                if rq:
                    if rq.status == RandomQuest.Status.ACCEPTED:
                        try:
                            extra = rq.clear()
                        except ValueError as e:
                            extra = {"detail": f"퀘스트 완료 처리 실패: {str(e)}"}
                    else:
                        extra = {"detail": "이미 완료된 퀘스트입니다."}

            else:
                receipt.status = Receipt.Status.FAILURE
                receipt.message = f"OCR 실패 ({response.status_code})"
                receipt.save()

            response_data = ReceiptSerializer(receipt).data
            if extra:
                response_data["extra"] = extra

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
