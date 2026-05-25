from django.urls import path
from . import views

urlpatterns = [
    path('', views.boyhome, name='boyhome'),
    path('dashboard/', views.boyhome, name='delivery_dashboard'),
    path('orders/', views.delivery_orders, name='delivery_orders'),
    path('orders/<int:order_id>/delivered/', views.mark_order_delivered, name='mark_order_delivered'),
    path('completed/', views.delivery_completed, name='delivery_completed'),
    path('locations/', views.delivery_locations, name='delivery_locations'),
    path('profile/', views.delivery_profile, name='delivery_profile'),
    path('history/', views.delivery_history, name='delivery_history'),
]
