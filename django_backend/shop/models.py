from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.utils.timezone import now
import uuid
import hashlib
from django.utils.text import slugify


class CustomerManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


# Custom User Model for Customer
class Customer(AbstractUser):
    username = models.CharField(max_length=150, unique=False, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'shop_customer'
        verbose_name = "Customer"
        verbose_name_plural = "Customers"


# Category Model
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'shop_category'
        verbose_name = "Category"
        verbose_name_plural = "Categories"


# Product Model
class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(stock__gte=0), name='stock_non_negative'),
        ]
        db_table = 'shop_product'
        verbose_name = "Product"
        verbose_name_plural = "Products"


# Cart Item Model
class CartItem(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

    class Meta:
        db_table = 'shop_cart_item'
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        ordering = ['added_at']


# Order Model
class Order(models.Model):
    STATUS_CHOICES = [("PENDING", "Pending"), ("COMPLETED", "Completed"), ("CANCELLED", "Cancelled")]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="orders")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    tracking_number = models.CharField(max_length=50, blank=True, null=True)  # Ensure this field is included

    def __str__(self):
        return f"Order {self.id} by {self.customer.email}"

    class Meta:
        db_table = 'shop_order'
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']


# Order Item Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in Order {self.order.id}"

    class Meta:
        db_table = 'shop_order_item'
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"


# Invoice Model
class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="invoice")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="invoices")
    issued_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Invoice {self.id} for Order {self.order.id}"

    class Meta:
        db_table = 'shop_invoice'
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        ordering = ['-issued_at']


# Payment Method Model
class PaymentMethod(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="payment_methods")
    method_type = models.CharField(
        max_length=50,
        choices=[
            ("CREDIT_CARD", "Credit Card"),
            ("DEBIT_CARD", "Debit Card"),
            ("BANK_ACCOUNT", "Bank Account")
        ]
    )
    number = models.CharField(max_length=20)
    added_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.number and len(self.number) > 4:
            self.number = self.mask_card_number_display()
        super().save(*args, **kwargs)

    def mask_card_number_display(self):
        if self.number and len(self.number) > 4:
            return '****-****-****-' + self.number[-4:]
        return self.number

    def __str__(self):
        return f"{self.method_type} ending with {self.number[-4:]}"

    class Meta:
        db_table = 'shop_payment_method'
        verbose_name = "Payment Method"
        verbose_name_plural = "Payment Methods"
        constraints = [
            models.UniqueConstraint(fields=['customer', 'method_type'],
                                    name='unique_customer_method')
        ]
        ordering = ['-added_at']


# Transaction Model
class Transaction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="transactions")
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="transactions")
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Transaction {self.transaction_id} for Order {self.order.id}"

    class Meta:
        db_table = 'shop_transaction'
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ['-transaction_date']


# Product Rating Model
class ProductRating(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="product_ratings")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    rated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating {self.rating} by {self.customer.email} for {self.product.name}"

    class Meta:
        db_table = 'shop_product_rating'
        verbose_name = "Product Rating"
        verbose_name_plural = "Product Ratings"
        ordering = ['-rated_at']


# Product Recommendation Model
class ProductRecommendation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="recommendations")
    recommended_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="recommended_by")

    def __str__(self):
        return f"Recommend {self.recommended_product.name} for {self.product.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['product', 'recommended_product'], name='unique_recommendation'),
            models.CheckConstraint(check=~models.Q(product=models.F('recommended_product')), name='check_product_ids'),
        ]
        db_table = 'shop_product_recommendation'
        verbose_name = "Product Recommendation"
        verbose_name_plural = "Product Recommendations"
        ordering = ['product']


# Address Model
class Address(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.country}"

    class Meta:
        db_table = 'shop_address'
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        ordering = ['-is_default', '-created_at']


# Coupon Model
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Coupon {self.code}"

    class Meta:
        db_table = 'shop_coupon'
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"
        ordering = ['-valid_from']