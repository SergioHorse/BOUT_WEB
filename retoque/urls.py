from django.urls import path
from . import views
from .views import RetoqueDetailView

urlpatterns = [

    path('retoques', views.summary, name='summary'),
    path('retoques/<int:pk>/', RetoqueDetailView.as_view(), name='detalle'),
    path('retoques/<int:pk>/edit/', views.edit_retouch, name='edit'),
]

