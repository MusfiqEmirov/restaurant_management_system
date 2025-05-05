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
    
    def get(self,request):
        #admin ve musteri mesajlari gormey ucun

        logger.debug(f"mesaj sorgulari gore siyahi alindi:{request.user.email}")
        try:
            user = request.user
            if user.role == "customer":
                #musteri yalniz oz mesajlarini gorer
                messages = Message.objects.filter(is_deleted=False).filter(Q(sender=user) | Q(recipient=user))
            else:
                if request.query_params.get("all") == "true":
                    #admin butun mesajlari gorur
                    messages = Message.objects.filter(is_deleted=False).filter(Q(sender=user | Q(recipient=user)))

            serializer = MessageSerializer(messages, many=True)
            logger.info(f"mesaj siyahisi qaytarildi:{user.email}, sayi:{messages.count()}")
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"mesaj siyahisi alinaerken xeta bas verdi:{str(e)}", exc_info=True)
            return Response({"error:" "mesaj siyahisi alinarken xeta bas verdi"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                            )
        
    def delete(self, request, message_id=None):
            """
            mesajin silinmesi
            musyteri yalniz oz mesajini sile biler
        admin her kesin mesajini sile biler
            """
            logger.debug(f"mesaj silme sorgusu alindi {request.user.email}, Mesaj ID: {message_id}")
            if not message_id:
                logger.error("mesaj id daxil edilmeyib.")
                return Response({'error': 'mesaj  id teleb olunur'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                message = Message.objects.filter(id=message_id, is_deleted=False).first()
                if not message:
                    logger.error(f"mesaj tapilmadi ID {message_id}")
                    return Response({'error': 'mesaj tapilmadi'}, status=status.HTTP_404_NOT_FOUND)

                user = request.user
                if user.role == 'customer' and message.sender != user:
                    logger.error(f"mesaji icazesiz silme cehdi {user.email}, Mesaj ID: {message_id}")
                    return Response({'error': 'yalniz oz mesajlariniiz sile bilkersiz.'},
                                    status=status.HTTP_403_FORBIDDEN
                                    )

                # admin he rkesin mesajini sile biler
                message.is_deleted = True
                message.save()
                logger.info(f"Mesaj silindi: {user.email}, Mesaj ID: {message_id}")
                return Response({'message': 'Mesaj ugurla silindi.'}, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Mesaji silerken xeta: {str(e)}", exc_info=True)
                return Response({'error': 'mesaj silerkne xeta bas verdi.'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                                )