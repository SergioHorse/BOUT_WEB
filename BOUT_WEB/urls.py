"""
URL configuration for BOUT_WEB project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Página principal: formulario de login
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),

    # Rutas de accounts que no duplican nombres (reset de contraseña, etc.)
    path('accounts/', include('django.contrib.auth.urls')),

    path('zaq/', include('zaq.urls')),
    path('retoques/', include('retoque.urls')),
    path('bancos/', include('bancos.urls')),
    path('gestion/', include('gestion_forms.urls')),
]

