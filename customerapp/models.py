from django.db import models
from adminapp.models import Customerreg, Order, OrderItem, Product

class CustomerRating(models.Model):
    rating_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customerreg, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'order_item')

    def __str__(self):
        return f"{self.customer.Customer_name} - {self.product.name} ({self.rating})"
