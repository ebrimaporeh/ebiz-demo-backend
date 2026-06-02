"""
Root URL configuration.

All API routes live under /api/v1/.
Add app-level URL includes here as apps are created.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # JWT auth
    path('api/v1/auth/token/',         TokenObtainPairView.as_view(),  name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(),     name='token_refresh'),
    path('api/v1/auth/token/verify/',  TokenVerifyView.as_view(),      name='token_verify'),

    # App routes — add as apps are built, e.g.:
    # path('api/v1/users/',    include('apps.users.urls')),
    # path('api/v1/datasets/', include('apps.datasets.urls')),
    # path('api/v1/pipeline/', include('apps.pipeline.urls')),
    # path('api/v1/audit/',    include('apps.audit.urls')),
    # path('api/v1/taxonomy/', include('apps.taxonomy.urls')),
    # path('api/v1/catalog/',  include('apps.catalog.urls')),
]
