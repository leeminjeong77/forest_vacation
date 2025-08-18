from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer

# 알람 목록 조회 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)

# 알람 읽기
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    notification = Notification.objects.filter(id=notification_id, user=request.user).first()
    
    if not notification:
        return Response({"error": "해당 알람이 없습니다."}, status=404)
    
    notification.is_read = True
    notification.save()
    
    return Response({"message": "알람을 읽음 처리했습니다."}, status=200)

# 읽은 알람 삭제 
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_read_notifications(request):
    deleted_count, _ = Notification.objects.filter(user=request.user, is_read=True).delete()
    return Response({"message": f"{deleted_count}개의 읽은 알람이 삭제되었습니다."})