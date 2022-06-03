from django.contrib import admin
from .models import Hall, MaterialsPrices, MaterialsAmount


class MaterialsForProject(admin.TabularInline):
    model = MaterialsAmount


@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ['project_id', 'salesman', 'calculated_value', 'update_date']
    list_filter = ['salesman', 'calculated_value', 'update_date']
    inlines = [
        MaterialsForProject
    ]


@admin.register(MaterialsPrices)
class MaterialsPricesAdmin(admin.ModelAdmin):
    list_display = ['material_id', 'material', 'update_date']


@admin.register(MaterialsAmount)
class MaterialsAmountAdmin(admin.ModelAdmin):
    list_display = ['amount_id', 'project', 'material', 'amount']
    list_filter = ['material', 'project']
