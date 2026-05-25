from django.urls import path
from . import views
urlpatterns = [
    path('cuthome/', views.cuthome, name='cuthome'),
    path('item', views.item, name='item'),
    path('cutcategory/', views.cutcategory, name='cutcategory'),
    path('category_products/<int:id>/', views.category_products, name='category_products'),
    path('customer_profile/', views.customer_profile, name='customer_profile'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('update-cart/<int:cart_id>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('buy_now/<int:id>/', views.buy_now, name='buy_now'),
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('order-success/', views.order_success, name='order_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('feedback/<int:order_item_id>/', views.customer_feedback, name='customer_feedback'),
]
