import uuid
import logging
import stripe
from rest_framework import viewsets, status, generics, serializers, permissions
from rest_framework.serializers import Serializer as EmptySerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from rest_framework.reverse import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from .models import (
    Customer, CartItem, Order as ShopOrder, PaymentMethod, Transaction,
    Invoice, ProductRating, ProductRecommendation, Product, Category, Order,
    OrderItem, Address, Coupon
)
from .serializers import (
    CustomerSerializer, CartItemSerializer, OrderSerializer, PaymentMethodSerializer,
    TransactionSerializer, InvoiceSerializer, 
    ProductRatingSerializer,
    ProductSerializer, ProductRecommendationSerializer, CategorySerializer,
    StockUpdateSerializer,
    AddressSerializer, CouponSerializer, RegisterSerializer, LoginSerializer,
    OrderItemSerializer, EmptySerializer
)
from django.utils import timezone
from rest_framework.decorators import action
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.password_validation import validate_password
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse

User = get_user_model()

logger = logging.getLogger(__name__)

# Stripe API Configuration
stripe.api_key = settings.STRIPE_SECRET_KEY

# Utility Functions
def generate_tracking_number():
    return f"TRACK-{uuid.uuid4().hex.upper()[:10]}"  # Example implementation

def handle_payment_intent_succeeded(payment_intent):
    try:
        transaction = Transaction.objects.get(stripe_payment_intent_id=payment_intent['id'])
        order = transaction.order
        order.status = 'COMPLETED'
        order.tracking_number = generate_tracking_number()
        order.save()
        logger.info(f"Order {order.id} marked as COMPLETED.")
    except Transaction.DoesNotExist:
        logger.error(f"No transaction found for PaymentIntent ID {payment_intent['id']}")

# API Endpoints

# Homepage View
def homepage(request):
    return render(request, 'endpoint_homepage.html')  # Ensure 'endpoint_homepage.html' exists

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return CartItem.objects.none()
        if self.request.user.is_staff:
            return self.queryset  # Admin users can see all cart items
        return self.queryset.filter(customer=self.request.user)

    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']
        if product.stock < quantity:
            raise serializers.ValidationError("Not enough stock available.")
        product.stock -= quantity
        product.save()
        serializer.save(customer=self.request.user)

    def perform_update(self, serializer):
        instance = self.get_object()
        product = serializer.validated_data['product']
        new_quantity = serializer.validated_data['quantity']
        old_quantity = instance.quantity
        quantity_difference = new_quantity - old_quantity
        if product.stock < quantity_difference:
            raise serializers.ValidationError("Not enough stock available.")
        product.stock -= quantity_difference
        product.save()
        serializer.save()

    def perform_destroy(self, instance):
        product = instance.product
        product.stock += instance.quantity
        product.save()
        instance.delete()

class CartItemDetailView(generics.RetrieveAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]  # Ensure only authenticated users can access

class CartItemCreateView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]  # Ensure only authenticated users can create

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # Associate cart item with the authenticated user

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        if self.request.user.is_staff:
            return self.queryset  # Admin users can see all orders
        return self.queryset.filter(customer=self.request.user)

    def perform_create(self, serializer):
        order = serializer.save(customer=self.request.user)
        for item in order.order_items.all():
            product = item.product
            if product.stock < item.quantity:
                raise serializers.ValidationError(f"Not enough stock for {product.name}.")
            product.stock -= item.quantity
            product.save()

class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return PaymentMethod.objects.none()
        return self.queryset.filter(customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Transaction.objects.none()
        return self.queryset.filter(customer=self.request.user)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAdminUser]

class InvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing invoices.
    """
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Invoice.objects.none()
        return self.queryset.filter(customer=self.request.user)

class ProductRatingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product ratings.
    """
    queryset = ProductRating.objects.all()
    serializer_class = ProductRatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ProductRating.objects.none()
        return self.queryset.filter(customer=self.request.user)

class ProductRecommendationViewSet(viewsets.ModelViewSet):
    queryset = ProductRecommendation.objects.all()
    serializer_class = ProductRecommendationSerializer
    filterset_fields = ['product__name', 'recommended_product__name']
    search_fields = ['product__name', 'recommended_product__name']
    ordering_fields = ['product__name']

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = ['category__name', 'price']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def update_stock(self, request, pk=None):
        product = self.get_object()
        serializer = StockUpdateSerializer(data=request.data)
        if serializer.is_valid():
            product.stock = serializer.validated_data['stock']
            product.save()
            return Response({'status': 'stock updated', 'stock': product.stock})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_fields = ['name']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at']

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    filterset_fields = ['customer__username', 'city', 'country']
    search_fields = ['customer__username', 'street', 'city', 'country']
    ordering_fields = ['is_default', 'created_at']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Address.objects.none()
        return Address.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)
        logger.info(f"Address created for user: {self.request.user.email}")

class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    filterset_fields = ['code', 'active']
    search_fields = ['code', 'description']
    ordering_fields = ['valid_from', 'valid_to', 'discount_amount']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Coupon.objects.none()
        return Coupon.objects.filter(active=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now())

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'id': user.id,
            'email': user.email,
        }, status=status.HTTP_200_OK)

class LogoutView(generics.GenericAPIView):
    serializer_class = EmptySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False):
            return Response()  # Return an empty response for schema generation
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=204)
        except Exception:
            return Response(status=400)

    def get_serializer_class(self):
        if getattr(self, 'swagger_fake_view', False):
            return EmptySerializer
        return super().get_serializer_class()

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    filterset_fields = ['order__id', 'product__name']
    search_fields = ['order__id', 'product__name']
    ordering_fields = ['price', 'quantity']

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if new_password != confirm_password:
            return Response({'detail': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Password changed successfully.'}, status=status.HTTP_200_OK)

class CreatePaymentIntentView(APIView):
    def post(self, request):
        try:
            amount = int(request.data.get('amount'))  # Amount in cents
            order_id = request.data.get('order_id')
            order = Order.objects.get(id=order_id)
            
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='usd',
                metadata={'order_id': order_id},
            )
            
            return Response({'client_secret': intent.client_secret}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            order_id = payment_intent['metadata']['order_id']
            order = Order.objects.get(id=order_id)
            Transaction.objects.create(
                order=order,
                payment_method=None,  # Update if applicable
                customer=order.customer,
                transaction_id=payment_intent['id'],
                amount=payment_intent['amount'] / 100,
                stripe_payment_intent_id=payment_intent['id'],
            )
            order.status = 'COMPLETED'
            order.save()
        # ... handle other event types ...

        return Response(status=status.HTTP_200_OK)

class OrderListView(generics.ListAPIView):
    """
    API view to retrieve list of orders for the authenticated customer.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        return Order.objects.filter(customer=self.request.user)

class OrderDetailView(generics.RetrieveAPIView):
    """
    API view to retrieve a specific order by ID for the authenticated customer.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        return Order.objects.filter(customer=self.request.user)

class CreateOrderView(generics.CreateAPIView):
    """
    API view to create a new order for the authenticated customer.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)