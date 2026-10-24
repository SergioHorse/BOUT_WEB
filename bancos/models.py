from django.db import models
from django.conf import settings
from django.utils import timezone

from simple_history.models import HistoricalRecords

# Create your models here.

class EstadoRodaje(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name='Estado de rodaje')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Estado de rodaje'
        verbose_name_plural = 'Estados de rodaje'
        permissions = [
            ('view_estado_rodaje', 'Puede cambiar el estado de rodaje'),
        ]

class Rodaje(models.Model):

    engine = models.ForeignKey(
        'zaq.Engine',
        on_delete=models.PROTECT,
        related_name='bancos',
        verbose_name='Motor',
    )

    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Rodador',
    )

    status = models.ForeignKey(
        EstadoRodaje,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Estado actual',
    )

    resultado = models.CharField(verbose_name='Resultado', null=True, blank=True,
                                 choices=[('OK','OK'),('NOK','NOK')])

    observations = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    date_analysis = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de rodaje')

    history = HistoricalRecords()


    def save(self, *args, **kwargs):

        if self.resultado in ('OK','NOK'):
            self.date_analysis = timezone.now()

        super().save(*args, **kwargs)




    def __str__(self):
        return f'{self.engine.n_engine} - {self.engine.reference}'