
from django.db import models
from django.contrib.auth.models import User
import string
import random
from datetime import datetime    
from datetime import date


class Material_Inventory(models.Model):
    pt = (('inward', 'inward'), ('outward', 'outward'))
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='material_user')
    item_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    in_out = models.CharField(max_length=10, choices=pt)
    comment = models.CharField(max_length=100)
    date = models.DateField(("Date"), default=date.today)
    inventory_category = models.CharField(max_length=50)
    def __str__(self):
            return self.inventory_category  + " -> " + self.item_name + " ("  + str(self.quantity) +  ") " + " :: "  +self.in_out


class Components_List(models.Model):
    item_name = models.CharField(max_length=100)
    standard_inventory_to_maintain = models.PositiveIntegerField()
    inventory_category = models.CharField(max_length=50)
    def __str__(self):
        return self.inventory_category  + " -> " + self.item_name + " (Minimum quantity to be maintained : "  + str(self.standard_inventory_to_maintain) +  ") "


class Category_List(models.Model):
    Categories = models.CharField(max_length=100)
    def __str__(self):
        return self.Categories







