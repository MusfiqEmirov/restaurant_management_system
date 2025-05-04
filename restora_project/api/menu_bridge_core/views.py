from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from project_apps.menu.models import (Category,
                                      MenuItem
                                      )
from project_apps.menu.serializers import (CategorySerializer,
                                           MenuItemSerializer
                                           )
from project_apps.core.logging import get_logger

logger = get_logger(__name__)


class CategoryView(APIView):
    def get(self, request, category_id=None):
        """
        categoriyalari ve siyahisni qaytarir
        Hher kes baxa biler icaze teleb olunmur
        """
        logger.debug(f"kategoriya sorgusu alindi: {request.user.email if request.user.is_authenticated else 'Qonaq'}, ID: {category_id}")
        try:
            if category_id:
                category = Category.objects.filter(id=category_id, is_deleted=False).first()
                if not category:
                    logger.error(f"Kateqoriya tapilmadi: ID {category_id}")
                    return Response({'error': 'categoriya tapilmadi'}, status=status.HTTP_404_NOT_FOUND)
                serializer = CategorySerializer(category)
                logger.info(f"ketgoriya detali tapildi: ID {category_id}")
                return Response(serializer.data, status=status.HTTP_200_OK)

            categories = Category.objects.filter(is_deleted=False)
            serializer = CategorySerializer(categories, many=True)
            logger.info(f"kategoriya siyahisni geri qaytarildi: say: {categories.count()}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"categroiya shiyasini yaranan zaman xeta: {str(e)}", exc_info=True)
            return Response({'error': 'categroiya shiyasini yaranan zaman xeta'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """
        yeni categroiya yaratmag yalniz adminler
        """
        logger.debug(f"kategoriya sorgusu alindi: {request.data}")
        if not request.user.is_authenticated or request.user.role != 'admin':
            logger.error(f"categoriya yaratmgcun icazniz yoxdur: {request.user.email if request.user.is_authenticated else 'Qonaq'}")
            return Response({'error': 'categoriya yaratmgcun icazniz yoxdur.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            try:
                category = serializer.save()
                logger.info(f"Kateqoriya yaradildi: {category.name}, Admin: {request.user.email}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Kateqoriya yadadileerken xeta bas verdi xeta: {str(e)}", exc_info=True)
                return Response({'error': 'Kateqoriya yadadileerken xeta bas verdi xeta:'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.error(f"serilizer xetasi : {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, category_id=None):
        """
        categoriyalri yenilemek ancaq adminler terefinnen
        """
        if not category_id:
            logger.error("categroiya ID daxil edilmeyib")
            return Response({'error': 'kategiryaya id teleb olunur'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_authenticated or request.user.role != 'admin':
            logger.error(f"yenilemek ucun izaceniz yoxdur: {request.user.email if request.user.is_authenticated else 'Qonaq'}, ID: {category_id}")
            return Response({'error': 'yenielemk ucun izaceniz yoxdur.'}, status=status.HTTP_403_FORBIDDEN)

        logger.debug(f"kategoriya yenilemek sorgusu alindi: {request.user.email}, ID: {category_id}")
        try:
            category = Category.objects.filter(id=category_id, is_deleted=False).first()
            if not category:
                logger.error(f"kategoriya tapilmadi ID {category_id}")
                return Response({'error': 'kategoriya tapilmadi '}, status=status.HTTP_404_NOT_FOUND)

            serializer = CategorySerializer(category, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Kateqoriya yenilendi: {category.name}, Admin: {request.user.email}")
                return Response(serializer.data, status=status.HTTP_200_OK)
            logger.error(f"Serializer xetasi bas verdi: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Kateqoriya yenilenerken xeta: {str(e)}", exc_info=True)
            return Response({'error': 'Kateqoriya yenilenerken xeta.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, category_id=None):
        """
        categoriyalari ancaq adminler sile biler
        """
        if not category_id:
            logger.error("categroiya ID daxil edilmeyib")
            return Response({'error': 'categroiya ID daxil edilmeyib'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_authenticated or request.user.role != 'admin':
            logger.error(f"icaze olmadan categoriya siline bilmez: {request.user.email if request.user.is_authenticated else 'Qonaq'}, ID: {category_id}")
            return Response({'error': 'icaze olmadan categoriya siline bilmez: yalniz admin'}, status=status.HTTP_403_FORBIDDEN)

        logger.debug(f"Kateqoriya silmek ucub sorgu alindi: {request.user.email}, ID: {category_id}")
        try:
            category = Category.objects.filter(id=category_id, is_deleted=False).first()
            if not category:
                logger.error(f"Kateqoriya tapilmadi ID {category_id}")
                return Response({'error': 'Kateqoriya tapilmadi!'}, status=status.HTTP_404_NOT_FOUND)

            category.is_deleted = True
            category.save()
            logger.info(f"Kateqoriya silindi: {category.name}, Admin: {request.user.email}")
            return Response({'message': 'Kateqoriya ugutla silindi.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Kateqoriya silerken xeta: {str(e)}", exc_info=True)
            return Response({'error': 'Kateqoriya silerken xeta:'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MenuItemView(APIView):
    def get(self, request, item_id=None):
        # menyunu her kes gore biler
        
        logger.debug(f"menyu elementi sorgusu alindi: {request.user.email if request.user.is_authenticated else 'Qonaq'}, ID: {item_id}")
        try:
            if item_id:
                item = MenuItem.objects.filter(id=item_id, is_deleted=False).first()
                if not item:
                    logger.error(f"Menyu elementi yoxdur: ID {item_id}")
                    return Response({'error': 'Menyu elementi yoxdur:'}, status=status.HTTP_404_NOT_FOUND)
                serializer = MenuItemSerializer(item)
                logger.info(f"Menyu elementi detali qaytarildi ID {item_id}")
                return Response(serializer.data, status=status.HTTP_200_OK)

            items = MenuItem.objects.filter(is_deleted=False)
            serializer = MenuItemSerializer(items, many=True)
            logger.info(f"Menyu elementi siyahisi qaytaildi say: {items.count()}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"xeta bas veerdi siyahi alinarken: {str(e)}", exc_info=True)
            return Response({'error': 'xeta bas veerdi siyahi alinarken:'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """
        menu elementi yaratm ancaa adminle
        """
        logger.debug(f"Menyu elementi yaratma sorgusu alindi: {request.data}")
        if not request.user.is_authenticated or request.user.role != 'admin':
            logger.error(f"menu yaratmag ancaa admine mexsusudur: {request.user.email if request.user.is_authenticated else 'Qonaq'}")
            return Response({'error': 'yalniz adminler menu elementi yarada biler'}, status=status.HTTP_403_FORBIDDEN)

        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            try:
                item = serializer.save()
                logger.info(f"Menyu elementi yaradildi: {item.name}, Admin: {request.user.email}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Menyu elementi yaradarken xeta: {str(e)}", exc_info=True)
                return Response({'error': 'Menyu elementi yaranerken xeta bas verdi'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.error(f"Serializer xetasi: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, item_id=None):
        """
        menyu elementi yenilemek yalniz adminler
        """
        if not item_id:
            logger.error("Menyu elementi ucun id daxil edilmeyib.")
            return Response({'error': 'Menyu elementi ucun id daxil edilmeyib'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_authenticated or request.user.role != 'admin':
            logger.error(f"icazesiz menyu elementi deyiwe bilmez: {request.user.email if request.user.is_authenticated else 'Qonaq'}, ID: {item_id}")
            return Response({'error': 'icazesiz menyu elementi deyiwe bilmez yalniz admin.'}, status=status.HTTP_403_FORBIDDEN)

        logger.debug(f"Menyu elementi sorgusu alindi: {request.user.email}, ID: {item_id}")
        try:
            item = MenuItem.objects.filter(id=item_id, is_deleted=False).first()
            if not item:
                logger.error(f"Menyu elementi tapilmadi: ID {item_id}")
                return Response({'error': 'Menyu elementi tapilmadi.'}, status=status.HTTP_404_NOT_FOUND)

            serializer = MenuItemSerializer(item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Menyu elementi yenilendi: {item.name}, Admin: {request.user.email}")
                return Response(serializer.data, status=status.HTTP_200_OK)
            logger.error(f"Serializer xetasi: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Menyu elementi yenilenerken xeta: {str(e)}", exc_info=True)
            return Response({'error': 'Menyu elementi yenilenerken xeta:'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, item_id=None):
        """
       menyu elementini silmek yalniz admiler
        """
        if not item_id:
            logger.error("Menyu elementi ucun Id daxil edilmeyib")
            return Response({'error': 'Menyu elementi ucun Id daxil edilmeyib"'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_authenticated or request.user.role != 'admin':
            logger.error(f"icazzeniz olmadan menyu sile bilzmezsinizi: {request.user.email if request.user.is_authenticated else 'Qonaq'}, ID: {item_id}")
            return Response({'error': 'yalniz adminler menyu sile biler'}, status=status.HTTP_403_FORBIDDEN)

        logger.debug(f"admin elementi silme sorgusu alindi: {request.user.email}, ID: {item_id}")
        try:
            item = MenuItem.objects.filter(id=item_id, is_deleted=False).first()
            if not item:
                logger.error(f"menyu elementi tapilmadi: ID {item_id}")
                return Response({'error': 'menyu elementi tapilmadi'}, status=status.HTTP_404_NOT_FOUND)

            item.is_deleted = True
            item.save()
            logger.info(f"Menyu mehsulu silindi: {item.name}, Admin: {request.user.email}")
            return Response({'message': 'Menyu mehsulu ugurla silindi.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Menyu mehsulu silerkne xeta:{str(e)}", exc_info=True)
            return Response({'error': 'Menyu mehsulu silerkne xeta:'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)