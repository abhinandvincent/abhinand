from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.name
class User(models.Model):
    login_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=50)
    status = models.CharField(max_length=25)
class  Disctrict(models.Model):
    name = models.CharField(max_length=100)

class Location(models.Model):
    name = models.CharField(max_length=100)
    district = models.ForeignKey(Disctrict, on_delete=models.CASCADE, null=True, blank=True)

class Customerreg(models.Model):
    Customer_id = models.AutoField(primary_key=True)
    Customer_name = models.CharField(max_length=100)
    Email = models.EmailField()
    Location_id = models.ForeignKey(Location, on_delete=models.CASCADE)
    District_id = models.ForeignKey(Disctrict, on_delete=models.CASCADE)
    login_id = models.ForeignKey(User, on_delete=models.CASCADE)
    Contact = models.CharField(max_length=15,null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    address = models.TextField(max_length=255, null=True, blank=True)

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100)
    category_image = models.ImageField(upload_to='category_images/', null=True, blank=True)

class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customerreg, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)


class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customerreg, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField()
    contact = models.CharField(max_length=15)
    pincode = models.CharField(max_length=10)
    payment_method = models.CharField(max_length=20)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, default='Conformed')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Order #{self.order_id}"


class OrderItem(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    def __str__(self):
        return f"{self.product_name} ({self.quantity})"

class DeliveryBoy(models.Model):
    deliveryboy_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    profile_picture = models.ImageField(upload_to='deliveryboy_profiles/', null=True, blank=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=50)
    status = models.CharField(max_length=25)
