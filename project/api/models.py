from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token


# Creates token for new user
@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


# Makes email field mandatory
User._meta.get_field('email')._unique = True
User._meta.get_field('email').blank = False
User._meta.get_field('email').null = False


class MaterialsPrices(models.Model):
    material_id = models.AutoField(primary_key=True)
    material = models.CharField(max_length=32)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    update_date = models.DateField(auto_now=True)

    def __str__(self):
        return f'{self.material_id} - {self.material}'


class Hall(models.Model):
    project_id = models.AutoField(primary_key=True)
    salesman = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    length = models.DecimalField(max_digits=5, decimal_places=2)
    width = models.DecimalField(max_digits=5, decimal_places=2)
    pole_height = models.DecimalField(max_digits=4, decimal_places=2)
    roof_slope = models.SmallIntegerField()
    update_date = models.DateField(auto_now=True)
    calculated_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f'{self.project_id}'


class MaterialsAmount(models.Model):
    amount_id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Hall, on_delete=models.CASCADE)
    material = models.ForeignKey(MaterialsPrices, on_delete=models.SET_NULL, null=True)
    amount = models.SmallIntegerField()
    update_date = models.DateField(auto_now=True)

    def __str__(self):
        return f'{self.project} - {self.material}'
