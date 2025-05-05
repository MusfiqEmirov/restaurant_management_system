from django.db.models import Q 
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
        Sending message between customer and admin
        """
        logger.debug(f"Message request received {request.data}")
        serializer = MessageSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                message = serializer.save()
                logger.info(f"Message sent {request.user.email} -> {message.recipient.email}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error sending message: {str(e)}", exc_info=True)
                return Response({'error': 'Error occurred while sending the message.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.error(f"Serializer error {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        # For admin and customer to view their messages

        logger.debug(f"Message query received for listing: {request.user.email}")
        try:
            user = request.user
            if user.role == "customer":
                # Customer can only see their own messages
                messages = Message.objects.filter(is_deleted=False).filter(Q(sender=user) | Q(recipient=user))
            else:
                if request.query_params.get("all") == "true":
                    # Admin can see all messages
                    messages = Message.objects.filter(is_deleted=False).filter(Q(sender=user) | Q(recipient=user))

            serializer = MessageSerializer(messages, many=True)
            logger.info(f"Message list returned: {user.email}, count: {messages.count()}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error occurred while retrieving message list: {str(e)}", exc_info=True)
            return Response({"error": "Error occurred while retrieving message list."}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                            )
        
    def delete(self, request, message_id=None):
            """
            Deleting a message
            Customer can only delete their own messages
            Admin can delete any message
            """
            logger.debug(f"Delete message request received {request.user.email}, Message ID: {message_id}")
            if not message_id:
                logger.error("Message ID not provided.")
                return Response({'error': 'Message ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                message = Message.objects.filter(id=message_id, is_deleted=False).first()
                if not message:
                    logger.error(f"Message not found ID {message_id}")
                    return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)

                user = request.user
                if user.role == 'customer' and message.sender != user:
                    logger.error(f"Unauthorized attempt to delete message {user.email}, Message ID: {message_id}")
                    return Response({'error': 'You can only delete your own messages.'},
                                    status=status.HTTP_403_FORBIDDEN
                                    )

                # Admin can delete any message
                message.is_deleted = True
                message.save()
                logger.info(f"Message deleted: {user.email}, Message ID: {message_id}")
                return Response({'message': 'Message deleted successfully.'}, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error occurred while deleting message: {str(e)}", exc_info=True)
                return Response({'error': 'Error occurred while deleting the message.'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                                )
