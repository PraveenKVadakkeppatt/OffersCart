from django.urls import path

from .import views

urlpatterns = [
    path('place_order/',views.place_order,name='place_order'),
    path('payments/',views.payments,name='payments'),
    path('order_completed/',views.order_completed,name='order_completed'),
    path('apply_coupon',views.apply_coupon,name='apply_coupon'),
    path('remove_coupon',views.remove_coupon,name="remove_coupon"),
]

