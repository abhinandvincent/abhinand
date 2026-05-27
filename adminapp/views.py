from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
import smtplib
from email.message import EmailMessage
from django.db import transaction
from .models import Product
from .models import User
from .models import Disctrict
from .models import Location
from .models import Customerreg
from .models import Category
from .models import Order
from .models import DeliveryBoy
from django.db.models import F
from .models import Cart, OrderItem
from django.http import JsonResponse
from django.db.models import Sum
import json


def mainpage(request):
    return render(request, 'mainpage.html')


def addproduct(request):
    categories = Category.objects.all()
    return render(request, 'admin/addproduct.html', {
        'categories': categories
    })

def add_product(request):
    categories = Category.objects.all()

    if request.method == 'POST':
        pro_name = request.POST.get('product_name')
        pro_description = request.POST.get('product_description')
        pro_price = request.POST.get('product_price')
        pro_image = request.FILES.get('product_image')
        category_id = request.POST.get('category')
        quantity = request.POST.get('quantity')
        if Product.objects.filter(name=pro_name).exists():
            return HttpResponse("<script>alert('Product already exists!');window.location='/addproduct/';</script>")
        if pro_name and pro_price and category_id and quantity:
            
            category = Category.objects.get(category_id=category_id)  

            product = Product(   
                name=pro_name,
                description=pro_description,
                price=pro_price,
                image=pro_image,
                category=category,
                quantity=quantity
            )
            product.save()

            return redirect('product_list')

    return render(request, 'admin/addproduct.html', {
        'categories': categories
    })


def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    return render(request, 'admin/productlist.html', {'products': products, 'categories': categories})


def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()

    if request.method == 'POST':
        product.name = request.POST.get('product_name')
        product.description = request.POST.get('product_description')
        product.price = request.POST.get('product_price')
        category_id = request.POST.get('category')
        product.category = Category.objects.filter(category_id=category_id).first() if category_id else None

        if request.FILES.get('product_image'):
            product.image = request.FILES.get('product_image')

        product.save()
        return redirect('product_list')

    return render(request, 'admin/edit.html', {
        'product': product,
        'categories': categories
    })


def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('product_list')
def login_view(request):
    return render(request, 'guest/login.html')
def indexpage(request):
    return render(request, 'admin/indexpage.html')
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password')
    
        user = User.objects.filter(username=username, password=password).first()
        if user:
            request.session['username'] = user.username
            request.session['loginid'] = user.login_id
            if user.role == 'Admin':
                return redirect('adminindex')
            if user.role == 'Customer':
                return redirect('cuthome')
            if user.role == 'DeliveryBoy':
                return redirect('delivery_dashboard')
            else:
                return render(request, "guest/login.html", {"error": "Unauthorized access"})
        
        delivery_boy = DeliveryBoy.objects.filter(username=username, password=password).first()
        if delivery_boy:
            request.session['username'] = delivery_boy.username
            request.session['deliveryboy_id'] = delivery_boy.deliveryboy_id
            return redirect('delivery_dashboard')
        else:
            return render(request, "guest/login.html", {"error": "Invalid username or password"})
    return render(request, "guest/login.html")

def logout(request):
    request.session.flush()
    return redirect('login')

def dashboard(request):
    products = Product.objects.all()
    return render(request, 'admin/dashboard.html', {'products': products})
def adminheader(request):
    return render(request, 'admin/adminheader.html')
def adminindex(request):
    total_products = Product.objects.count()
    active_orders = Order.objects.exclude(status='Delivered').count()
    gross_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    registered_clients = Customerreg.objects.count()
    delivery_staff = DeliveryBoy.objects.count()
    recent_orders = Order.objects.select_related('customer').order_by('-created_at')[:5]

    return render(request, 'admin/adminindex.html', {
        'total_products': total_products,
        'active_orders': active_orders,
        'gross_revenue': gross_revenue,
        'registered_clients': registered_clients,
        'delivery_staff': delivery_staff,
        'recent_orders': recent_orders,
    })

def order_product_chart(request):
    product_orders = list(
        OrderItem.objects.values('product_name')
        .annotate(
            ordered_quantity=Sum('quantity'),
            sales_amount=Sum('total_price')
        )
        .order_by('-ordered_quantity')
    )

    labels = [item['product_name'] for item in product_orders]
    quantities = [item['ordered_quantity'] for item in product_orders]
    total_quantity = sum(quantities)
    total_sales = sum(item['sales_amount'] for item in product_orders)

    return render(request, 'admin/chart.html', {
        'product_orders': product_orders,
        'chart_labels': json.dumps(labels),
        'chart_values': json.dumps(quantities),
        'total_quantity': total_quantity,
        'total_sales': total_sales,
    })

def adminproductlist(request):
    products = Product.objects.all()
    return render(request, 'guest/guestproductlist.html', {'products': products})
def add_district(request):
    if request.method == 'POST':
        district_name = request.POST.get('district_name')
        if Disctrict.objects.filter(name=district_name).exists():
            return HttpResponse("<script>alert('District already exists!');window.location='/add_district/';</script>")
        if district_name:
            Disctrict.objects.create(name=district_name)  
            return redirect('adminindex')

    return render(request, 'admin/add_district.html')

def category(request):
    if request.method == "POST":
        category_name = request.POST.get('category_name')
        category_image = request.FILES.get('category_image') 
        if Category.objects.filter(category_name=category_name).exists():
            return HttpResponse("<script>alert('Category already exists!');window.location='/category/';</script>")
        if category_name:
            Category.objects.create(
                category_name=category_name,  
                category_image=category_image 
            )
            return redirect('category')

    return render(request, 'admin/category.html')

def edit_category(request, category_id):
    category_obj = get_object_or_404(Category, category_id=category_id)

    if request.method == "POST":
        category_name = request.POST.get('category_name')
        category_image = request.FILES.get('category_image')

        if Category.objects.filter(category_name=category_name).exclude(category_id=category_id).exists():
            return HttpResponse("<script>alert('Category already exists!');window.location='/catlist/';</script>")

        if category_name:
            category_obj.category_name = category_name
            if category_image:
                category_obj.category_image = category_image
            category_obj.save()
            return redirect('catlist')

    return render(request, 'admin/category.html', {
        'category_obj': category_obj,
        'is_edit': True
    })

def delete_category(request, category_id):
    category_obj = get_object_or_404(Category, category_id=category_id)

    if request.method == "POST":
        Product.objects.filter(category=category_obj).delete()
        category_obj.delete()
        return redirect('catlist')

    return redirect('catlist')

def add_location(request):
    districts = Disctrict.objects.all()

    if request.method == "POST":
        location_name = request.POST.get('location_name')
        district_id = request.POST.get('district')
        if Location.objects.filter(name=location_name, district_id=district_id).exists():
            return HttpResponse("<script>alert('Location already exists in this district!');window.location='/add_location/';</script>")
        if location_name and district_id: 
            Location.objects.create(
                name=location_name,
                district_id=district_id
            )
            return redirect('add_location')
    return render(request, 'admin/add_location.html', {'districts': districts})


def customer_register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            return HttpResponse("<script>alert('Username already exists!');window.location='/customer_register/';</script>")
        loginob = User()
        loginob.username = username
        loginob.password = password
        loginob.role = 'Customer'
        loginob.status = 'confirmed'
        loginob.save()

        custobj = Customerreg()
        custobj.Customer_name = request.POST.get('name')
        custobj.Email = request.POST.get('email')
        custobj.Contact = request.POST.get('contact')
        custobj.Location_id = Location.objects.get(id=request.POST.get('location'))
        custobj.District_id = Disctrict.objects.get(id=request.POST.get('district'))
        custobj.login_id = loginob
        custobj.pincode = request.POST.get('pincode')
        custobj.address = request.POST.get('address')
        custobj.save()

        return HttpResponse("<script>alert('Customer registered successfully!');window.location='/login/';</script>")

    districts = Disctrict.objects.all()
    locations = Location.objects.all()

    return render(request, 'guest/customer_register.html', {
        'districts': districts,
        'locations': locations
    })

def catlist(request):
        categories = Category.objects.all()
        return render(request, 'admin/catlist.html', {'categories': categories})

def services(request):   
    return render(request, 'guest/service.html')


def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'admin/adminorder_list.html', {
        'orders': orders
    })


def order_details(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    items = order.items.all()
    return render(request, 'admin/adminorder.html', {
        'order': order,
        'items': items,
        'customer': order.customer
    })

def place_order(request):
    if request.method == "POST":

        customer = Customerreg.objects.get(login_id=request.session['loginid'])
        cart_items = Cart.objects.filter(customer=customer)
        if not cart_items.exists():
            return HttpResponse("Cart is empty")
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        contact = request.POST.get('phone')
        pincode = request.POST.get('pincode')
        payment_method = request.POST.get('payment_type')
        total = sum(item.price * item.quantity for item in cart_items)
        order = Order.objects.create(
            customer=customer,
            name=name,
            email=email,
            address=address,
            contact=contact,
            pincode=pincode,
            payment_method=payment_method,
            total_amount=total
        )
        from django.db.models import F
        for item in cart_items:
            product = item.product
            if product.quantity < item.quantity:
                return HttpResponse(f"Not enough stock for {product.name}")
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                quantity=item.quantity,
                price=product.price,
                total_price=product.price * item.quantity
            )
            product.quantity = F('quantity') - item.quantity
            product.save()
        cart_items.delete()
        return redirect('order_list')
    return redirect('order_list')

def location_list(request):
    districts = Disctrict.objects.all()
    return render(request, 'admin/location_list.html', {'districts': districts})
  
def filllocation(request):
    did = request.POST.get('did')
    if did:
        locations = Location.objects.filter(district_id=did).values('id', 'name')
        location_list = [{'locationid': loc['id'], 'locationname': loc['name']} for loc in locations]
        return JsonResponse(location_list, safe=False)
    return JsonResponse([], safe=False)  

def fillcategory(request):
    cid = request.POST.get('cid')
    if cid:
        categories = Category.objects.filter(category_id=cid).values('category_id', 'category_name')
        category_list = [{'categoryid': cat['category_id'], 'categoryname': cat['category_name']} for cat in categories]
        return JsonResponse(category_list, safe=False)

def deliveryboy(request):
    if request.method == "POST":
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        address = request.POST.get('address')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists() or DeliveryBoy.objects.filter(username=username).exists():
            return HttpResponse("<script>alert('Username already exists!');window.location='/add_deliveryboy/';</script>")

        if name and contact and email and address and username and password:
            with transaction.atomic():
                User.objects.create(
                    username=username,
                    password=password,
                    role='DeliveryBoy',
                    status='confirmed'
                )
                DeliveryBoy.objects.create(
                    name=name,
                    contact=contact,
                    email=email,
                    address=address,
                    username=username,
                    password=password,
                    role='DeliveryBoy',
                    status='confirmed'
                )

            delivery_boy_email = email
            delivery_boy_name = name
            print(delivery_boy_email)
            msg = EmailMessage()
            msg.set_content(
                f"""Dear {delivery_boy_name},

Thank you for registering with Delivery System.

Your account has been successfully created.

Username : {username}

Password : {password}

Best regards,
Delivery Team"""
            )

            msg['Subject'] = 'Registration Completed'
            msg['From'] = 'abhinandvincent2006@gmail.com'
            msg['To'] = delivery_boy_email

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(
                    'abhinandvincent2006@gmail.com',
                    'vlml rlbd voqv dfav'
                )
                smtp.send_message(msg)

            return HttpResponse("<script>alert('Delivery boy added successfully!');window.location='/add_deliveryboy/';</script>")

    return render(request, 'admin/add_boy.html') 

def delivaryboy(request):
    return deliveryboy(request)
