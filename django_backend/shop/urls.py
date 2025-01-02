from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, CategoryViewSet, CustomerViewSet,
    OrderViewSet, OrderItemViewSet, InvoiceViewSet,
    TransactionViewSet, PaymentMethodViewSet, ProductRatingViewSet,
    ProductRecommendationViewSet, CartItemViewSet, AddressViewSet,
    CouponViewSet, RegisterView, LoginView, LogoutView, ChangePasswordView,
    CreatePaymentIntentView, StripeWebhookView, OrderListView, OrderDetailView, CreateOrderView,
    CartItemDetailView, CartItemCreateView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Initialize the router
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet, basename='orderitem')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'payment-methods', PaymentMethodViewSet, basename='paymentmethod')
router.register(r'product-ratings', ProductRatingViewSet, basename='productrating')
router.register(r'product-recommendations', ProductRecommendationViewSet, basename='productrecommendation')
router.register(r'cart-items', CartItemViewSet, basename='cartitem')
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'coupons', CouponViewSet, basename='coupon')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # JWT Authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('create-payment-intent/', CreatePaymentIntentView.as_view(), name='create_payment_intent'),
    path('stripe-webhook/', StripeWebhookView.as_view(), name='stripe_webhook'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<int:id>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/create/', CreateOrderView.as_view(), name='order-create'),
    path('cart-items/<int:pk>/', CartItemDetailView.as_view(), name='cartitem-detail'),
    path('cart-items/', CartItemCreateView.as_view(), name='cartitem-create'),
]
