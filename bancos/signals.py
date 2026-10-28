
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from zaq.models import Engine
from .models import Rodaje, EstadoRodaje


@receiver(pre_save, sender=Engine)
def check_category(sender, instance, **kwargs):
    categoria_anterior = None

    if instance.pk:
        instance._pre_category = (
            Engine.objects.filter(pk=instance.pk)
            .values_list('category_id', flat=True)
            .first()
        )
    instance._pre_category = categoria_anterior

    if (
        instance.category_id and instance.category.name == 'Azul' and categoria_anterior != instance.category_id
    ):
        instance.status = 'Pendiente de rodaje'


@receiver(post_save, sender=Engine)
def create_rodaje(sender, instance, created, **kwargs):
    if not instance.category or instance.category.name != 'Azul':
        return

    Rodaje.objects.get_or_create(engine=instance)