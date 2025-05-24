from django.urls import path
from .views import (CustomerView,
                    CustomerDiscountCodeView,
                    BonusRedeemView
                    )

urlpatterns = [
    path('', CustomerView.as_view(), name='customer_list'),
    path('<int:customer_id>/', CustomerView.as_view(), name='customer_detail'),
    path('discount/', CustomerDiscountCodeView.as_view(), name='customer_discount'),
    path('bonus/redeem/', BonusRedeemView.as_view(), name='bonus_redeem'),
]