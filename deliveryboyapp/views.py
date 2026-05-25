from django.shortcuts import get_object_or_404, redirect, render
from adminapp.models import DeliveryBoy, Order
from django.utils import timezone

def get_logged_in_delivery_boy(request):
    deliveryboy_id = request.session.get('deliveryboy_id')
    username = request.session.get('username')

    if deliveryboy_id:
        delivery_boy = DeliveryBoy.objects.filter(deliveryboy_id=deliveryboy_id).first()
        if delivery_boy:
            return delivery_boy

    if username:
        return DeliveryBoy.objects.filter(username=username).first()

    return None

def boyhome(request):
    today = timezone.localdate()

    assigned_orders = Order.objects.exclude(status='Delivered').count()
    completed_deliveries = Order.objects.filter(
        status='Delivered',
        created_at__year=today.year,
        created_at__month=today.month
    ).count()
    active_locations = Order.objects.exclude(status='Delivered').values('pincode').distinct().count()
    today_total = Order.objects.filter(created_at__date=today).count()
    today_delivered = Order.objects.filter(status='Delivered', created_at__date=today).count()
    daily_completion = round((today_delivered / today_total) * 100) if today_total else 0

    return render(request, 'deliveryboy/boyhome.html', {
        'delivery_boy': get_logged_in_delivery_boy(request),
        'assigned_orders': assigned_orders,
        'completed_deliveries': completed_deliveries,
        'active_locations': active_locations,
        'today_delivered': today_delivered,
        'today_total': today_total,
        'daily_completion': daily_completion,
    })

def delivery_orders(request):
    orders = Order.objects.exclude(status='Delivered').order_by('-created_at')
    return render(request, 'deliveryboy/boyorderlist.html', {
        'orders': orders
    })

def delivery_completed(request):
    orders = Order.objects.filter(status='Delivered').order_by('-created_at')
    return render(request, 'deliveryboy/boyorderlist.html', {
        'orders': orders,
        'completed_view': True
    })

def mark_order_delivered(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)

    if request.method == 'POST':
        order.status = 'Delivered'
        order.save()

    return redirect('delivery_orders')

def delivery_locations(request):
    return render(request, 'deliveryboy/boyhome.html')

def delivery_profile(request):
    delivery_boy = get_logged_in_delivery_boy(request)

    if not delivery_boy:
        return redirect('login')

    if request.method == 'POST' and request.FILES.get('profile_picture'):
        delivery_boy.profile_picture = request.FILES.get('profile_picture')
        delivery_boy.save()
        return redirect('delivery_profile')

    return render(request, 'deliveryboy/boyprofile.html', {
        'delivery_boy': delivery_boy
    })

def delivery_history(request):
    return render(request, 'deliveryboy/boyhome.html')
