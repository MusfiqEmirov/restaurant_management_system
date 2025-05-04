from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from project_apps.notifications.models import Message
from project_apps.notifications.serializers import MessageSerializer

from project_apps.core.logging import get_logger

logger = get_logger(__name__)

class MessageCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        musteri ve admin mesaji goindeirlme
        """
        logger.debug(f"mesaj sorgusu alindi {request.data}")
        serializer = MessageSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                message = serializer.save()
                logger.info(f"mesaj gonderildi{request.user.email} -> {message.recipient.email}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"mesaj gonderme xetasi: {str(e)}", exc_info=True)
                return Response({'error': 'Mmesaj gonderme zamani xeta bas verdi.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.error(f"serializer xetasi {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)