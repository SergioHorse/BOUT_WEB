from django.urls import path

from . import views

urlpatterns = [
    path(
        'engine/register',
        views.register_engine,
        name='register_engine',
    ),

    path(
        'engine/<int:category_id>/details/',
        views.engine_details,
        name='engine_details',
    ),
]