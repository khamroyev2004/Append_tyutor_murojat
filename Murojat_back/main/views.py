from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Message, Message_File
from account.models import User
from .serializer import *
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    recipient_id = request.data.get('recipient')
    content = request.data.get('content', '').strip()
    files = request.FILES.getlist('files')

    if not recipient_id:
        return Response({"error": "recipient majburiy"}, status=400)

    try:
        recipient = User.objects.get(id=recipient_id)
    except User.DoesNotExist:
        return Response({"error": "Qabul qiluvchi topilmadi"}, status=404)

    if not content and not files:
        return Response({"error": "Xabar matni yoki fayl bo‘lishi kerak"}, status=400)

    message = Message.objects.create(
        sender=request.user,
        recipient=recipient,
        content=content
    )

    for f in files:
        Message_File.objects.create(message=message, file=f)

    # ✅ WEBSOCKET REAL-TIME YUBORISH
    channel_layer = get_channel_layer()
    ids = sorted([request.user.id, recipient.id])
    room_name = f"chat_{ids[0]}_{ids[1]}"

    async_to_sync(channel_layer.group_send)(
        room_name,
        {
            "type": "chat_message",
            "message": MessageSerializer(
                message,
                context={"request": request}
            ).data
        }
    )

    return Response(
        MessageSerializer(message, context={"request": request}).data,
        status=201
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dialog(request, user_id):
    try:
        other_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {"error": "Foydalanuvchi topilmadi"},
            status=status.HTTP_404_NOT_FOUND
        )
    messages = Message.objects.filter(
        Q(sender=request.user, recipient=other_user) |
        Q(sender=other_user, recipient=request.user)
    ).order_by("timestamp")

    serializer = MessageSerializer(
        messages,
        many=True,
        context={"request": request}
    )
    return Response(serializer.data, status=status.HTTP_200_OK)



