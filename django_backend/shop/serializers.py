import logging
from rest_framework import serializers
from .models import (
    Customer, CartItem, Order, OrderItem, Invoice,
    PaymentMethod, Transaction, ProductRating, Product, ProductRecommendation, Category,
    Address, Coupon
)
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import authenticate

logger = logging.getLogger(__name__)

# Serializer for Product
class ProductSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Product
        fields = ['product_id', 'name', 'description', 'price', 'stock', 'category', 'created_at', 'image']

# Serializer for Category
class CategorySerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Category
        fields = ['category_id', 'name', 'description', 'created_at']

# Serializer for Address
class AddressSerializer(serializers.ModelSerializer):
    address_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Address
        fields = ['address_id', 'street', 'city', 'state', 'postal_code', 'country', 'is_default', 'created_at']

# Serializer for PaymentMethod
class PaymentMethodSerializer(serializers.ModelSerializer):
    payment_method_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = PaymentMethod
        fields = ['payment_method_id', 'customer', 'method_type', 'number', 'added_at']

# Serializer for CartItem
class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'

# Serializer for OrderItem
class OrderItemSerializer(serializers.ModelSerializer):
    order_item_id = serializers.IntegerField(source='id', read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    order_id = serializers.IntegerField(source='order.id', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['order_item_id', 'order_id', 'product_id', 'quantity', 'price']

# Serializer for Order
class OrderSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='id', read_only=True)
    customer_id = serializers.IntegerField(source='customer.id', read_only=True)
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['order_id', 'customer_id', 'total_amount', 'status', 'created_at', 'order_items']
        read_only_fields = ['order_id', 'customer_id', 'total_amount', 'status', 'created_at', 'order_items']

    def create(self, validated_data):
        customer = self.context['request'].user
        order = Order.objects.create(customer=customer, status='PENDING')
        # Additional logic to calculate total_amount can be added here
        return order

# Serializer for Transaction
class TransactionSerializer(serializers.ModelSerializer):
    transaction_id = serializers.IntegerField(source='id', read_only=True)
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    customer_id = serializers.IntegerField(source='customer.id', read_only=True)
    payment_method_id = serializers.IntegerField(source='payment_method.id', read_only=True)

    class Meta:
        model = Transaction
        fields = ['transaction_id', 'order_id', 'customer_id', 'payment_method_id', 'amount', 'transaction_date', 'stripe_payment_intent_id']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['payment_method'] = PaymentMethodSerializer(instance.payment_method).data
        return rep

# Serializer for Invoice
class InvoiceSerializer(serializers.ModelSerializer):
    invoice_id = serializers.IntegerField(source='id', read_only=True)
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    customer_id = serializers.IntegerField(source='customer.id', read_only=True)

    class Meta:
        model = Invoice
        fields = ['invoice_id', 'order_id', 'customer_id', 'total_amount', 'issued_at']

# Serializer for ProductRating
class ProductRatingSerializer(serializers.ModelSerializer):
    product_rating_id = serializers.IntegerField(source='id', read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    customer_id = serializers.IntegerField(source='customer.id', read_only=True)
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = ProductRating
        fields = ['product_rating_id', 'product_id', 'customer_id', 'rating', 'rated_at', 'product_name']

    def get_product_name(self, obj):
        return obj.product.name

    def validate_product(self, value):
        if not Product.objects.filter(id=value.id).exists():
            raise ValidationError("Product does not exist")
        return value

# Serializer for ProductRecommendation
class ProductRecommendationSerializer(serializers.ModelSerializer):
    product_recommendation_id = serializers.IntegerField(source='id', read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    recommended_product_id = serializers.IntegerField(source='recommended_product.id', read_only=True)
    recommended_product_details = serializers.SerializerMethodField()

    class Meta:
        model = ProductRecommendation
        fields = ['product_recommendation_id', 'product_id', 'recommended_product_id', 'recommended_product_details']

    def get_recommended_product_details(self, obj):
        return ProductSerializer(obj.recommended_product).data

    def validate_product(self, value):
        if not Product.objects.filter(id=value.id).exists():
            raise ValidationError("Product does not exist")
        return value

    def validate_recommended_product(self, value):
        if not Product.objects.filter(id=value.id).exists():
            raise ValidationError("Recommended product does not exist")
        return value

# Serializer for Stock Update
class StockUpdateSerializer(serializers.Serializer):
    stock = serializers.IntegerField()

    def validate_stock(self, value):
        if value < 0:
            raise ValidationError("Stock value cannot be negative.")
        return value

# Serializer for Coupon
class CouponSerializer(serializers.ModelSerializer):
    coupon_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Coupon
        fields = ['coupon_id', 'code', 'description', 'discount_amount', 'valid_from', 'valid_to', 'active']

# Serializer for Checkout
class CheckoutSerializer(serializers.Serializer):
    payment_method_id = serializers.CharField()
    shipping_address_id = serializers.IntegerField()
    coupon_code = serializers.CharField(required=False, allow_blank=True)

    def validate_coupon_code(self, value):
        if value:
            try:
                coupon = Coupon.objects.get(code=value, active=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now())
            except Coupon.DoesNotExist:
                raise ValidationError("Invalid or expired coupon code.")
        return value

    def create(self, validated_data):
        # Implement checkout logic here
        pass

class RegisterSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(source='id', read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Customer
        fields = ['customer_id', 'username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = Customer.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        return user

from django.contrib.auth import get_user_model

Customer = get_user_model()

from rest_framework_simplejwt.tokens import RefreshToken

class LoginSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField(source='user.id', read_only=True)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(username=email, password=password)  # Uses email as username

        if not user:
            logger.warning(f"Failed login attempt for email: {email}")
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            logger.warning(f"Inactive user login attempt for email: {email}")
            raise serializers.ValidationError("User account is disabled.")
        
        return {
            'user': user,
            'refresh': str(RefreshToken.for_user(user)),
            'access': str(RefreshToken.for_user(user).access_token),
            'customer_id': user.id,
            'email': user.email,
        }

# Serializer for Customer
class CustomerSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(source='id', read_only=True)
    addresses = AddressSerializer(many=True, read_only=True)
    payment_methods = PaymentMethodSerializer(many=True, read_only=True)
    cart_items = CartItemSerializer(many=True, read_only=True)
    orders = OrderSerializer(many=True, read_only=True)
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = ['customer_id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'addresses', 'payment_methods', 'cart_items', 'orders', 'transactions']

    def validate_email(self, value):
        if Customer.objects.filter(email=value).exists():
            raise ValidationError("Email already in use")
        return value

# Empty Serializer
class EmptySerializer(serializers.Serializer):
    pass