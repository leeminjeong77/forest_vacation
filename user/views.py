from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login

from .serializers import UserSerializer, UserInfoSerializer

# Create your views here.
@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.save()
        user.set_password(request.data["password"])
        user.save()
        message = f"id: {user.id}번 사용자의 회원가입이 완료되었습니다."
        return Response(
            {
                "status": "success",
                "code": 201,
                "message": message,
                "user": UserInfoSerializer(user).data,
            },
            status=201,
        )
    # 유효성 검사 실패 시 자동 예외처리 됨


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    student_num = request.data.get("student_num")
    password = request.data.get("password")
    user = authenticate(username=student_num, password=password)

    if user is None:
        return Response(
            {"message": "학번 또는 비밀번호가 일치하지 않습니다."},
            status=401,
        )

    refresh = RefreshToken.for_user(user)
    update_last_login(None, user)
    return Response(
        {  
            "refresh_token": str(refresh),
            "access_token": str(refresh.access_token),
            "user": UserInfoSerializer(user).data,
        },
        status=200,
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get("refresh_token")
        token = RefreshToken(refresh_token)
        token.blacklist()  # 블랙리스트에 등록해 무효화

        return Response({"message": "로그아웃 성공"}, status=status.HTTP_205_RESET_CONTENT)
    except Exception:
        return Response({"error": "로그아웃 실패"}, status=status.HTTP_400_BAD_REQUEST)

class UserApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = request.user
        serializer = UserInfoSerializer(user)
        return Response(
            {"status": "success", "code": 200, "user": serializer.data},
            status=200,
        )

    def patch(self, request, pk):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            if "password" in request.data:
                user.set_password(request.data["password"])
                user.save()
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "code": 200,
                    "message": "회원 정보가 수정되었습니다.",
                    "user": UserInfoSerializer(user).data,
                },
                status=200,
            )

    def delete(self, request, pk):
        user = request.user
        user.delete()
        return Response(
            {"status": "success", "code": 200, "message": "회원 탈퇴가 완료되었습니다."}
        )

