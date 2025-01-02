from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin
import logging

from .models import (
    Customer, Category, CartItem, Order, Invoice, Transaction,
    PaymentMethod, OrderItem, ProductRating, ProductRecommendation, Product,
    Address, Coupon
)

logger = logging.getLogger(__name__)

class CustomerAdminForm(forms.ModelForm):
    """
    Custom form for Customer Admin to handle additional validations or fields.
    Ensures phone number starts with '+'.
    """
    class Meta:
        model = Customer
        fields = '__all__'

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone and not phone.startswith('+'):
            raise forms.ValidationError("Phone number must start with '+'")
        return phone

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'added_at')
    can_delete = False

class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')

class OrderInline(admin.StackedInline):
    model = Order
    extra = 0
    readonly_fields = ('status', 'total_amount', 'created_at')
    show_change_link = True

class PaymentMethodInline(admin.TabularInline):
    model = PaymentMethod
    extra = 0
    readonly_fields = ('id', 'customer', 'method_type', 'number', 'added_at')
    fields = ('id', 'customer', 'method_type', 'number', 'added_at')

class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    readonly_fields = ('street', 'city', 'state', 'postal_code', 'country', 'is_default', 'created_at')
    can_delete = False

class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    readonly_fields = ('transaction_id', 'amount', 'transaction_date', 'stripe_payment_intent_id')
    can_delete = False

class InvoiceInline(admin.TabularInline):
    model = Invoice
    extra = 0
    readonly_fields = ('order', 'customer', 'total_amount', 'issued_at')
    can_delete = False

class BaseAdmin(admin.ModelAdmin):
    list_display = ('id',)
    readonly_fields = ('id',)
    search_fields = ('id',)
    list_filter = ()
    ordering = ('-id',)

@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(BaseAdmin):
    list_display = ('id', 'name', 'description', 'price', 'stock', 'category', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('category', 'created_at')
    ordering = ('-created_at',)

@admin.register(CartItem)
class CartItemAdmin(BaseAdmin):
    list_display = ('id', 'customer', 'product', 'quantity', 'added_at')
    search_fields = ('customer__username', 'product__name')
    list_filter = ('customer', 'added_at')

@admin.register(Order)
class OrderAdmin(BaseAdmin):
    list_display = ('id', 'customer', 'total_amount', 'status', 'created_at')
    search_fields = ('customer__username', 'id')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]

@admin.register(Invoice)
class InvoiceAdmin(BaseAdmin):
    list_display = ('id', 'order', 'customer', 'total_amount', 'issued_at')
    search_fields = ('order__id', 'customer__username')
    list_filter = ('issued_at',)

@admin.register(Transaction)
class TransactionAdmin(BaseAdmin):
    list_display = ('id', 'order', 'transaction_id', 'amount', 'payment_method', 'transaction_date', 'stripe_payment_intent_id')
    search_fields = ('transaction_id', 'order__id', 'order__customer__username')
    list_filter = ('transaction_date',)

@admin.register(PaymentMethod)
class PaymentMethodAdmin(BaseAdmin):
    list_display = ('id', 'customer', 'method_type', 'masked_number', 'added_at')
    search_fields = ('customer__username', 'method_type')
    list_filter = ('method_type', 'added_at')

    def masked_number(self, obj):
        """
        Return a masked version of the payment method number.
        E.g., '****-****-****-1234'
        """
        if obj.number and len(obj.number) >= 4:
            masked = '****-****-****-' + obj.number[-4:]
            return masked
        return obj.number

    masked_number.short_description = 'Number'

@admin.register(ProductRating)
class ProductRatingAdmin(BaseAdmin):
    list_display = ('id', 'customer', 'product', 'rating', 'rated_at')

@admin.register(ProductRecommendation)
class ProductRecommendationAdmin(BaseAdmin):
    list_display = ('id', 'product', 'recommended_product')
    search_fields = ('product__name', 'recommended_product__name')

@admin.register(Address)
class AddressAdmin(BaseAdmin):
    list_display = ('id', 'customer', 'street', 'city', 'state', 'postal_code', 'country', 'is_default', 'created_at')
    search_fields = ('customer__username', 'street', 'city', 'country')
    list_filter = ('is_default', 'country')

@admin.register(Coupon)
class CouponAdmin(BaseAdmin):
    list_display = ('id', 'code', 'discount_amount', 'valid_from', 'valid_to', 'active')
    search_fields = ('code', 'description')
    list_filter = ('active', 'valid_from', 'valid_to')

@admin.register(Customer)
class CustomerAdmin(UserAdmin):
    form = CustomerAdminForm
    add_form = CustomerAdminForm  # Optional: specify another form for adding users
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone_number')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name', 'phone_number')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    inlines = [AddressInline, PaymentMethodInline, TransactionInline, OrderInline, InvoiceInline, CartItemInline]

