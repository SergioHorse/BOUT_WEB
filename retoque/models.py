from django.contrib.auth.models import Group
from django.db import models
from django.conf import settings
from django.utils import timezone

from simple_history.models import HistoricalRecords


class EstadoRetoque(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name='Estado de retoque')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Estado de retoque'
        verbose_name_plural = 'Estados de retoque'


class ImputacionRetoque(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name='Imputación de retoque')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Imputación de retoque'
        verbose_name_plural = 'Imputaciones de retoque'


class Retoque(models.Model):
    engine = models.ForeignKey(
        'zaq.Engine',
        on_delete=models.PROTECT,
        related_name='retoques',
        verbose_name='Motor',
    )
    status = models.ForeignKey(
        EstadoRetoque,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Estado actual',
    )
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Retocador',
    )
    observations = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    date_analysis = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de análisis')

    allocation_retouching_cost = models.ForeignKey(
        ImputacionRetoque,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name='Imputación del retoque',
    )

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        # Corrección: comprobar que status exista antes de leer .name
        if self.status and self.status.name == 'Terminado' and self.date_analysis is None:
            self.date_analysis = timezone.localdate()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.engine.n_engine} - {self.engine.reference}'


class CampoListado(models.Model):
    campo = models.CharField(max_length=100, unique=True, verbose_name='Campo')
    titulo = models.CharField(max_length=100, verbose_name='Titulo')
    visible = models.BooleanField(default=True)
    orden = models.PositiveSmallIntegerField(default=0)
    grupos = models.ManyToManyField(
        Group,
        blank=True,
        related_name='campos_retoque',
        verbose_name='Visible para grupos',
    )

    class Meta:
        ordering = ['campo', 'id']
        verbose_name = 'Campo'
        verbose_name_plural = 'Campos'

    def __str__(self):
        return self.titulo
