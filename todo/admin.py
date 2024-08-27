

from django.contrib import admin
from .models import Material_Inventory,Components_List,Category_List


@admin.register(Material_Inventory,Components_List,Category_List)
class PersonAdmin(admin.ModelAdmin):
    pass