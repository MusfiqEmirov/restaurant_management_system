from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum

from project_apps.orders.models import Order, OrderItem
from project_apps.orders.serializers import (OrderSerializer,
                                             OrderItemSerializer,
                                             SalesReportSerializer
                                            )
from project_apps.core.logging import get_logger

logger = get_logger(__name__)


class OrderView(APIView):
    # sifarisleirn soyasini detallarini gormek yenilemek silmek ve yaratmg ucun

    def get(self, request, order_id=None):
        # eger giris olunmayibsa
        if not request.user.is_authenticated:
            logger.error(f"baxiw ucun icaze lazimdir")
            return Response(
                {"error": "sifarisleri gormey ucun giris teleb olunur"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = request.user
        logger.debug(
            f"sifaris sorgusu alindi: {user.email}, ID: {order_id}, "
            f"parametrler: {request.query_params}"
        )

        if order_id:
            order = get_object_or_404(Order, id=order_id, is_deleted=False)
            if user.role == "customer" and order.user != user:
                logger.error(
                    f"sifarise baxmagcun admin ve ya staff olmag lazimdir{user.email}, sifaris ID: {order_id}"
                )
                return Response(
                    {"error": "yalniz musteri oz sifarisini gore biler"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = OrderSerializer(order)
            logger.info(f"sifaris detali qaytarildi: ID {order_id}")
            return Response(serializer.data, status=status.HTTP_200_OK)

        orders = Order.objects.filter(is_deleted=False)
        # eger istifadeci musteridirse
        if user.role == "customer":
            orders = orders.filter(user=user)
            #ger istifadeci admindirse
        elif user.role == "admin" and request.query_params:
            filter_serializer = SalesReportSerializer(data=request.query_params)
            if filter_serializer.is_valid():
                start_date = filter_serializer.validated_data.get("start_date")
                end_date = filter_serializer.validated_data.get("end_date")
                payment_type = filter_serializer.validated_data.get("payment_type")

                # baslangic tarix
                if start_date:
                    orders = orders.filter(created_at__date__gte=start_date)
                    #son tarix
                if end_date:
                    orders = orders.filter(created_at__date__lte=end_date)
                    #ondeis novune gore
                if payment_type:
                    orders = orders.filter(payment_type=payment_type)
            else:
                logger.error(f"filter analiz xetasi: {filter_serializer.errors}")
                return Response(
                    filter_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )

        serializer = OrderSerializer(orders, many=True)
        logger.info(f"sifarislerin siyahisi qaytarildi: say: {orders.count()}")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # sifaris ancaq admin ve staff terefinnen yaradila biler
        if not request.user.is_authenticated:
            logger.error(f"icazesiz yaratma cehdi: Qonaq")
            return Response(
                {"error": "sifaris yaratmagcun giriw teleb olunur"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if request.user.role not in ["admin", "staff"]:
            logger.error(
                f"giriw ucun icaze lazimdir: {request.user.email}, rol: {request.user.role}"
            )
            return Response(
                {"error": "yalniz admin ve staf sifaris yarada biler"},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data.copy()

        # musteri id daxil edilmezse
        if "user_id" not in data:
            logger.error(f"musteri idsi daxil edilmeyib: {request.user.email}")
            return Response(
                {"error": "sifaris ucun musteri idsi teleb olunur."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data["created_by_id"] = request.user.id

        serializer = OrderSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            order = serializer.save()
            logger.info(
                f"sifaris idisi yaradildi: ID {order.id}, "
                f"musteri: {order.user.email}, yaradan: {request.user.email}"
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Serializer xetasi: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, order_id=None):
        # sifaris ancaq admin ve staff terefinnen yenilene biler
        if not order_id:
            logger.error("sifaris idisi daxil edilmeyib")
            return Response(
                {"error": "sifarisidis teleb olunur."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not request.user.is_authenticated or request.user.role not in ["admin", "staff"]:
            logger.error(
                f"yenilemek ucun giriw lazimdir {request.user.email if request.user.is_authenticated else 'Qonaq'}, "
                f"rol: {request.user.role if request.user.is_authenticated else 'Yoxdur'}"
            )
            return Response(
                {"error": "yalniz admin ve ya staff yenileye biler"},
                status=status.HTTP_403_FORBIDDEN,
            )

        order = get_object_or_404(Order, id=order_id, is_deleted=False)
        serializer = OrderSerializer(
            order, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            logger.info(
                f"sifaris yenilendi: ID {order.id}, "
                f"musteri: {order.user.email}, yeniyelen: {request.user.email}"
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error(f"Serializer xetasi: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, order_id=None):
        # ancaq admin sile biler
        if not order_id:
            logger.error("sifaris daxil edilmeyib")
            return Response(
                {"error": "id teleb olunur sifaris ucun."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not request.user.is_authenticated or request.user.role not in ["admin", "staff"]:
            logger.error(
                f"silmek ucun firiw tmeyniz xahis olunur {request.user.email if request.user.is_authenticated else 'Qonaq'}, "
                f"rol: {request.user.role if request.user.is_authenticated else 'Yoxdur'}"
            )
            return Response(
                {"error": "yalniz admin sile biler"},
                status=status.HTTP_403_FORBIDDEN,
            )

        order = get_object_or_404(Order, id=order_id, is_deleted=False)
        if request.user.role == "admin":
            order.delete()
            logger.info(
                f"sifaris bir basa sikindi: ID {order.id}, "
                f"müştərmusterii: {order.user.email}, admin: {request.user.email}"
            )
            return Response(
                {"message": "sifaris tamamile silindi"},
                status=status.HTTP_200_OK,
            )
        else:  # staff
            order.is_deleted = True
            order.save()
            logger.info(
                f"sifaris soft silindi: ID {order.id}, "
                f"musteri: {order.user.email}, staff: {request.user.email}"
            )
            return Response(
                {"message": "sifaris soft silindi."},
                status=status.HTTP_200_OK,
            )

class OrderItemView(APIView):
    # sifaris elementlerinin siyahisi yenilenmesi silinmesi ve yaranamsi

    def get(self, request, item_id=None):
       # #sifaris elmentlernin siyashini qaytarrir
        if not request.user.is_authenticated:
            logger.error(f"icaze yoxdur: Qonaq")
            return Response(
                {"error": "giris edin sifarisleri gormey ucun"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = request.user
        logger.debug(
            f"sifarislerin sorgusu alindi: {user.email}, ID: {item_id}"
        )

        if item_id:
            item = get_object_or_404(OrderItem, id=item_id, is_deleted=False)
            if user.role == "customer" and item.order.user != user:
                logger.error(
                    f"giris etmeden baxmag olmaz oz sifarislerinize: {user.email}, element ID: {item_id}"
                )
                return Response(
                    {"error": "yalniz oz sifarislerinize bxa bilersiz."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = OrderItemSerializer(item)
            logger.info(f"sifarislerinize baxa bilersiz ID {item_id}")
            return Response(serializer.data, status=status.HTTP_200_OK)

        items = OrderItem.objects.filter(is_deleted=False)
        
        if user.role == "customer":
            items = items.filter(order__user=user)
        serializer = OrderItemSerializer(items, many=True)
        logger.info(f"sifarislerin siyahisi yaradildi: say: {items.count()}")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # yeni sifaris elementi yaratmag ancaq admin ve staff ile
        if not request.user.is_authenticated:
            logger.error(f"icaze yoxdur musteri ucun: Qonaq")
            return Response(
                {"error": "sifaris elementleri ucun giris edin"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if request.user.role not in ["admin", "staff"]:
            logger.error(
                f"giris ucun icaze lamzidir: {request.user.email}, rol: {request.user.role}"
            )
            return Response(
                {"error": "yalniz admin ve staff yarada biler"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = OrderItemSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            item = serializer.save()
            logger.info(
                f"sifaris elementi yaradildi: ID {item.id}, "
                f"menyu: {item.menu_item.name}, yaradan: {request.user.email}"
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Serializer xetasi: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, item_id=None):
        # sifaris elementlerini yelilemek hemcini admin ve staff ile
        if not item_id:
            logger.error("sifaris ucun id lazimdir")
            return Response(
                {"error": "sifrais elementleri ucun Id lazimdir"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not request.user.is_authenticated or request.user.role not in ["admin", "staff"]:
            logger.error(
                f"icazeniz yoxdur yenielemk ucun {request.user.email if request.user.is_authenticated else 'Qonaq'}, "
                f"rol: {request.user.role if request.user.is_authenticated else 'Yoxdur'}"
            )
            return Response(
                {"error": "yalniz admin ve ya staff yenileye biler."},
                status=status.HTTP_403_FORBIDDEN,
            )

        item = get_object_or_404(OrderItem, id=item_id, is_deleted=False)
        serializer = OrderItemSerializer(
            item, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            logger.info(
                f"sifaris elementleri yneilendi: ID {item.id}, "
                f"menyu: {item.menu_item.name}, yenileyen: {request.user.email}"
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error(f"Serializer xetasi: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, item_id=None):
        # sifaris elementlerini silen admin ve ya staff
        if not item_id:
            logger.error("ID daxil edilmeyib")
            return Response(
                {"error": "sifaris silmek ucun id lazimdir"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not request.user.is_authenticated or request.user.role not in ["admin", "staff"]:
            logger.error(
                f"iczae yoxdur silmek ucun{request.user.email if request.user.is_authenticated else 'Qonaq'}, "
                f"rol: {request.user.role if request.user.is_authenticated else 'Yoxdur'}"
            )
            return Response(
                {"error": "yalniz admin ve ya staff sile biler."},
                status=status.HTTP_403_FORBIDDEN,
            )

        item = get_object_or_404(OrderItem, id=item_id, is_deleted=False)
        if request.user.role == "admin":
            item.delete()
            logger.info(
                f"sifaris elementleri silindi: ID {item.id}, "
                f"menyu: {item.menu_item.name}, admin: {request.user.email}"
            )
            return Response(
                {"message": "sifaris elementleri silindi"},
                status=status.HTTP_200_OK,
            )
        else:  # staff
            item.is_deleted = True
            item.save()
            logger.info(
                f"sifaris elmeentleri soft silindi: ID {item.id}, "
                f"menyu: {item.menu_item.name}, staff: {request.user.email}"
            )
            return Response(
                {"message": "sifaris elementleri soft silindi"},
                status=status.HTTP_200_OK,
            )

class SalesReportView(APIView):
    # satis hesabatlarina baxmag ve filter elemek

    def get(self, request):
        # satis hesabatniin qaytarir
        if not request.user.is_authenticated or request.user.role != "admin":
            logger.error(
                f"giris ucunicaze yoxdur: {request.user.email if request.user.is_authenticated else 'Qonaq'}, "
                f"rol: {request.user.role if request.user.is_authenticated else 'Yoxdur'}"
            )
            return Response(
                {"error": "hesabata ancaq adminler bxa biler"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = SalesReportSerializer(data=request.query_params)
        if not serializer.is_valid():
            logger.error(f"hesabat serializer xetasi {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        start_date = data["start_date"]
        end_date = data["end_date"]
        payment_type = data.get("payment_type")

        orders = Order.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            is_deleted=False,
        )
        if payment_type:
            orders = orders.filter(payment_type=payment_type)

        total_amount = orders.aggregate(Sum("total_amount"))["total_amount__sum"] or 0
        order_count = orders.count()
        total_bonus_points = sum(order.calculate_bonus_points() for order in orders)

        report_data = {
            "start_date": start_date,
            "end_date": end_date,
            "payment_type": payment_type,
            "orders": OrderSerializer(orders, many=True).data,
            "total_amount": total_amount,
            "order_count": order_count,
            "total_bonus_points": total_bonus_points,
        }

        logger.info(
            f"satis hesabati hazirdi tarix {start_date} - {end_date}, "
            f"öodenis novu: {payment_type or 'hamisi'}, admin: {request.user.email}"
        )
        return Response(report_data, status=status.HTTP_200_OK)