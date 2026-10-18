from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from zaq.models import Engine
from .models import Retoque, EstadoRetoque


@receiver(pre_save, sender=Engine)
def check_category(sender, instance, **kwargs):

    instance._pre_category = None

    if instance.pk:
        instance._pre_category = {
            Engine.objects.filter(pk=instance.pk).values_list('category_id', flat=True).first()
        }

@receiver(post_save, sender=Engine)
def create_retoque(sender, instance,created, **kwargs):


    if instance.category.name == 'Amarillo':

        status = EstadoRetoque.objects.get(
            name = 'Pendiente'
        )

        retoque, created = Retoque.objects.get_or_create(
            engine=instance,
            defaults={
                'status': status,
            }
        )

        if created:
            print(f"Retoque creado: {retoque.id}")

