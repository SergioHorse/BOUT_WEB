from django.urls import path

from . import views

app_name = 'bancos'

urlpatterns = [

    path('create/', views.create_rodaje, name='create'),
    path('buscar_motor/', views.buscar_motor, name='buscar_motor'),
    path('summary/', views.summary, name='summary'),
    path('<int:pk>/', views.RodajeDetailView.as_view(), name='detail'),
    path('<int:pk>/editar/', views.RodajeUpdateView.as_view(), name='edit'),
    path('<int:pk>/eliminar/', views.RodajeDeleteView.as_view(), name='delete'),

]

