from django.db import models
from django.conf import settings
from django.db.models import Model

from simple_history.models import HistoricalRecords


# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)
    color = models.CharField(max_length=15,
                             default='#FFFFFF',
                             verbose_name='Color botón categoría')
    icon = models.CharField(max_length=50,
                            blank=True,
                            default='bi-box',
                            verbose_name="Icono")

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.name


class Detail(models.Model):
    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE,
                                 related_name='details')
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Detalle'
        verbose_name_plural = 'Detalles'

    def __str__(self):
        return self.name


class Engine(models.Model):
    code_bar = models.CharField(max_length=100,
                                unique=True,
                                verbose_name='Código de barras')

    reference = models.CharField(max_length=12,
                                 blank=True,
                                 verbose_name="Referencia")

    n_engine = models.CharField(max_length=7,
                                blank=True,
                                verbose_name="Nº motor")

    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE,
                                 related_name='engines',
                                 verbose_name='Categoría')

    details = models.ManyToManyField(Detail,
                                     related_name='engines',
                                     verbose_name='Detalles seleccionados')

    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Operario')

    date_created = models.DateTimeField(auto_now_add=True,
                                        verbose_name='Fecha de registro')

    status = models.CharField(max_length=50,
                              blank=True,
                              null=True,
                              default='Pendiente',
                              verbose_name="Estado actual")

    history = HistoricalRecords(m2m_fields=['details'])

    def save(self, *args, **kwargs):
        if self.code_bar:
            if 'RTD' in self.code_bar:
                reference, n_engine = self.code_bar.split('TD', 1)
                self.reference = reference
                self.n_engine = n_engine

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-date_created']
        verbose_name = 'Motor'
        verbose_name_plural = 'Motores'

    def __str__(self):
        return self.code_bar
