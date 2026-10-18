
from django.urls import path
from . import views

app_name = 'retoque'

urlpatterns = [
    path('', views.summary, name='summary'),
    path('nuevo/', views.RetoqueCreateView.as_view(), name='create'),
    path('<int:pk>/', views.RetoqueDetailView.as_view(), name='detail'),
    path('<int:pk>/editar/', views.RetoqueUpdateView.as_view(), name='edit'),
    path('<int:pk>/eliminar/', views.RetoqueDeleteView.as_view(), name='delete'),
]

