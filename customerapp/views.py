from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Avg, Count
from adminapp.models import Category, Customerreg, User, Product, Cart, Order, OrderItem
from .models import CustomerRating

def _rating_stars(average_rating):
    if average_rating is None:
        return '☆☆☆☆☆'

    rounded_rating = int(round(float(average_rating)))
    rounded_rating = max(0, min(5, rounded_rating))
    return '★' * rounded_rating + '☆' * (5 - rounded_rating)


def _attach_product_ratings(products):
    products = list(products)
    rating_rows = CustomerRating.objects.filter(product__in=products).values('product').annotate(
        average_rating=Avg('rating'),
        review_count=Count('rating')
    )
    ratings_by_product = {
        row['product']: row
        for row in rating_rows
    }

    for product in products:
        rating_info = ratings_by_product.get(product.id, {})
        average_rating = rating_info.get('average_rating')
        product.average_rating = average_rating
        product.review_count = rating_info.get('review_count', 0)
        product.rating_stars = _rating_stars(average_rating)

    return products

def cuthome(request):

    return render(request, 'customer/cuthome.html')

def item(request):
    return render(request, 'customer/items.html')

def cutcategory(request):
    categories = Category.objects.all()
    return render(request, 'customer/cutcategory.html', {'categories': categories})
    
def category_products(request, id):
    category = get_object_or_404(Category, pk=id)
    products = _attach_product_ratings(Product.objects.filter(category=category))

    return render(request, 'customer/category_products.html', {
        'category': category,
        'products': products
    })

def customer_profile(request):
    username = request.session.get('username')
    if not username:
        return redirect('login')  # Assuming there's a login URL
    
    user = get_object_or_404(User, username=username)
    customer = get_object_or_404(Customerreg, login_id=user)
    
    return render(request, 'customer/profile.html', {'customer': customer})

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    reviews = CustomerRating.objects.filter(product=product).select_related('customer').order_by('-created_at')
    average_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
    product.rating_stars = _rating_stars(average_rating)
    product.review_count = reviews.count()
    return render(request, 'customer/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'average_rating': average_rating
    })

def add_to_cart(request, id):
    if request.method != 'POST':
        return redirect('product_detail', id=id)

    login_id = request.session.get('loginid')

    if not login_id:
        messages.error(request, 'Please login to add items to cart')
        return redirect('login')

    customer = Customerreg.objects.filter(login_id_id=login_id).first()

    if not customer:
        messages.error(request, 'Customer profile not found. Please contact support.')
        return redirect('cuthome')

    product = get_object_or_404(Product, id=id)

    quantity = request.POST.get('quantity', 1)
    try:
        quantity = int(quantity)
    except:
        quantity = 1

    if quantity < 1:
        quantity = 1

    cart_item, created = Cart.objects.get_or_create(
        customer=customer,
        product=product,
        defaults={
            'price': product.price,
            'quantity': quantity
        }
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.price = product.price
        cart_item.save()

    messages.success(request, f'{product.name} added to cart successfully!')
    return redirect('cart')

def cart(request):
    login_id = request.session.get('loginid')

    if not login_id:
        return render(request, 'customer/cart.html', {
            'cart_items': [],
            'subtotal': 0,
            'total': 0,
        })

    customer = Customerreg.objects.filter(login_id_id=login_id).first()

    if not customer:
        return render(request, 'customer/cart.html', {
            'cart_items': [],
            'subtotal': 0,
            'total': 0,
        })

    cart_items = Cart.objects.filter(customer=customer).select_related('product')

    subtotal = 0

    for item in cart_items:
        item.total_price = item.quantity * item.price
        subtotal += item.total_price

    return render(request, 'customer/cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': subtotal,
    })

def update_cart(request, cart_id):
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        try:
            quantity = int(quantity)
            if quantity < 1:
                quantity = 1
        except:
            quantity = 1

        cart_item = get_object_or_404(Cart, cart_id=cart_id)
        cart_item.quantity = quantity
        cart_item.save()

    return redirect('cart')

def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, cart_id=cart_id)
    cart_item.delete()
    return redirect('cart')
def buy_now(request, id):
    if request.method != 'POST':
        return redirect('product_detail', id=id)

    login_id = request.session.get('loginid')

    if not login_id:
        messages.error(request, 'Please login to buy items')
        return redirect('login')

    customer = Customerreg.objects.filter(login_id_id=login_id).first()

    if not customer:
        messages.error(request, 'Customer profile not found. Please contact support.')
        return redirect('cuthome')

    product = get_object_or_404(Product, id=id)

    quantity = request.POST.get('quantity', 1)
    try:
        quantity = int(quantity)
    except:
        quantity = 1

    if quantity < 1:
        quantity = 1

    messages.success(request, f'You have successfully bought {quantity} of {product.name}!')
    return redirect('cuthome')

def checkout(request):
    login_id = request.session.get('loginid')

    if not login_id:
        return redirect('login')

    customer = Customerreg.objects.filter(login_id_id=login_id).first()

    if not customer:
        messages.error(request, 'Customer profile not found. Please contact support.')
        return redirect('cuthome')

    cart_items = Cart.objects.filter(customer=customer).select_related('product')

    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')

    subtotal = 0

    for item in cart_items:
        item.total_price = item.quantity * item.price
        subtotal += item.total_price

    return render(request, 'customer/checkout.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': subtotal,
        'customer': customer,
    })

def place_order(request):
    if request.method != 'POST':
        return redirect('checkout')

    login_id = request.session.get('loginid')

    if not login_id:
        return redirect('login')

    customer = Customerreg.objects.filter(login_id_id=login_id).first()

    if not customer:
        return redirect('cuthome')

    cart_items = Cart.objects.filter(customer=customer)

    if not cart_items:
        messages.error(request, "Cart is empty")
        return redirect('cart')

    total = 0
    for item in cart_items:
        total += item.quantity * item.price

    order = Order.objects.create(
        customer=customer,
        name=request.POST.get('name'),
        email=request.POST.get('email'),
        address=request.POST.get('address'),
        contact=request.POST.get('phone'),
        pincode=request.POST.get('pincode'),
        payment_method=request.POST.get('payment_type'),
        total_amount=total
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name=item.product.name,
            quantity=item.quantity,
            price=item.price,
            total_price=item.quantity * item.price
        )
    for item in cart_items:
        product = item.product
        if product.quantity >= item.quantity:
            product.quantity -= item.quantity
            product.save()
        else:
            product.quantity = 0
            product.save()
    cart_items.delete()
    messages.success(request, "Order placed successfully!")
    return redirect('order_success')
    
def order_success(request):
    return render(request, 'customer/order_success.html')

def my_orders(request):
    login_id = request.session.get('loginid')
    if not login_id:
        return redirect('login')
    customer = Customerreg.objects.filter(login_id_id=login_id).first()
    if not customer:
        return redirect('login')
    orders = list(
        Order.objects.filter(customer=customer)
        .prefetch_related('items__product')
        .order_by('-created_at')
    )
    order_items = [
        item
        for order in orders
        for item in order.items.all()
    ]
    rated_item_ids = set(
        CustomerRating.objects.filter(
            customer=customer,
            order_item__in=order_items
        ).values_list('order_item_id', flat=True)
    )

    for item in order_items:
        item.feedback_registered = item.order_item_id in rated_item_ids

    return render(request, 'customer/my_orders.html', {
        'orders': orders
    })

def customer_feedback(request, order_item_id):
    login_id = request.session.get('loginid')
    if not login_id:
        return redirect('login')

    customer = Customerreg.objects.filter(login_id_id=login_id).first()
    if not customer:
        return redirect('login')

    order_item = get_object_or_404(
        OrderItem,
        order_item_id=order_item_id,
        order__customer=customer,
        order__status='Delivered'
    )

    if CustomerRating.objects.filter(customer=customer, order_item=order_item).exists():
        messages.info(request, "Your feedback is already registered for this item.")
        return redirect('my_orders')

    if request.method == 'POST':
        rating = request.POST.get('rating')
        feedback = request.POST.get('feedback')

        if not rating or not feedback:
            messages.error(request, "Please add rating and feedback.")
            return redirect('customer_feedback', order_item_id=order_item.order_item_id)

        CustomerRating.objects.create(
            customer=customer,
            order_item=order_item,
            product=order_item.product,
            order=order_item.order,
            rating=rating,
            feedback=feedback
        )
        messages.success(request, "Your feedback is registered successfully.")
        return redirect('my_orders')

    return render(request, 'customer/feedback.html', {
        'order': order_item.order,
        'order_item': order_item
    })
