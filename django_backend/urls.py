from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from shop.views import homepage
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.views.generic import TemplateView

# Swagger and ReDoc schema view
schema_view = get_schema_view(
    openapi.Info(
        title="GreenCart API",
        default_version='v1',
        description="API documentation for GreenCart",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@greencart.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Use the custom Swagger UI template with correct context
    path(
        'swagger/',
        TemplateView.as_view(
            template_name="swagger/swagger-ui.html",
            extra_context={'schema_url': 'schema-json'}
        ),
        name='swagger-ui'
    ),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('accounts/', include('django.contrib.auth.urls')),  # Add Django auth URLs for login/logout and password reset
    path('', homepage, name='homepage'),  # Render the homepage
    # JWT Authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Include the shop URLs without the /api/ prefix
    path('', include('shop.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
