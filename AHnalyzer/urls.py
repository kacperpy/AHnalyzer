"""AHnalyzer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django_registration.backends.one_step.views import RegistrationView

from users.forms import CustomUserForm

from core.views import IndexTemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/register/',
        RegistrationView.as_view(form_class=CustomUserForm, success_url='/'),
        name='django_registration_register'),
    path('accounts/', include('django.contrib.auth.urls')),

    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

    path('api/v1/items/', include("items.api.urls", namespace='items')),
    path('api/v1/users/', include("users.api.urls", namespace='users')),

    re_path(r"^.*$", IndexTemplateView.as_view(), name="spa-entry-point")
]
