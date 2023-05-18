from django.db import models
from django.utils import timezone


class Place(models.Model):
    address = models.CharField(max_length=100, unique=True, verbose_name="адрес")
    lon = models.DecimalField(max_digits=8, decimal_places=5)
    lat = models.DecimalField(max_digits=8, decimal_places=5)
    registrated_at = models.DateTimeField(default=timezone.now, verbose_name="дата")

    class Meta:
        verbose_name = "Место"
        verbose_name_plural = "Места"

    def __str__(self):
        return self.address
