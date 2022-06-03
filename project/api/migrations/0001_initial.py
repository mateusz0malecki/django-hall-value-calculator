# Generated by Django 4.0.5 on 2022-06-03 16:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Hall',
            fields=[
                ('project_id', models.AutoField(primary_key=True, serialize=False)),
                ('length', models.DecimalField(decimal_places=2, max_digits=5)),
                ('width', models.DecimalField(decimal_places=2, max_digits=5)),
                ('pole_height', models.DecimalField(decimal_places=2, max_digits=4)),
                ('roof_slope', models.SmallIntegerField()),
                ('update_date', models.DateField(auto_now=True)),
                ('calculated_value', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('salesman', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MaterialsPrices',
            fields=[
                ('material_id', models.AutoField(primary_key=True, serialize=False)),
                ('material', models.CharField(max_length=32)),
                ('price', models.DecimalField(decimal_places=2, max_digits=7)),
                ('update_date', models.DateField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='MaterialsAmount',
            fields=[
                ('amount_id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.SmallIntegerField()),
                ('update_date', models.DateField(auto_now=True)),
                ('material', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.materialsprices')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.hall')),
            ],
        ),
    ]