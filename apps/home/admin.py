# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin

# Register your models here.
from . import models

# @admin.register(models.Recents)
# class RecentsAdmin(admin.ModelAdmin):
#     list_display = ('created_at', 'updated_at')

@admin.register(models.Student)
class HomeAdmin(admin.ModelAdmin):
    list_display = ("Student_number", "First_name", "Last_name", "Year_level", "Corporate_email", "Password")
    search_fields = ("Student_number", "First_name", )

@admin.register(models.Officer)
class HomeAdmin(admin.ModelAdmin):
    list_display = ("Student", "Position")
    search_fields = ("Student", )

@admin.register(models.FeeType)
class HomeAdmin(admin.ModelAdmin):
    list_display = ("Fee_name", "Fee_amount")
    search_fields = ("Fee_name", )

@admin.register(models.Transaction)
class HomeAdmin(admin.ModelAdmin):
    list_display = ("Student", "Transaction_date", "Payment_type", "Amount", "Status")
    search_fields = ("Student", "Transaction_date", "Payment_type", )

# @admin.register(models.admin)
# class HomeAdmin(admin.ModelAdmin):
#     list_display = ("first_name", "last_name", "position", "email", "created_at","updated_at")
#     search_fields = ("first_name", )
    
# @admin.register(models.DueType)
# class HomeAdmin(admin.ModelAdmin):
#     list_display = ("type", "fees" ,"created_at")
#     search_fields = ("type", )
    
# @admin.register(models.Balance)
# class HomeAdmin(admin.ModelAdmin):
#     list_display = ("student", "amount", "type")
#     search_fields = ("student", )
    
# @admin.register(models.transaction)
# class HomeAdmin(admin.ModelAdmin):
#     list_display = ("payee", "receiver", "dueType", "date")
#     search_fields = ("payee", "receiver")

# @admin.register(models.Event)
# class HomeAdmin(admin.ModelAdmin):
#     list_display = ("event_name", "date", "announcement")
#     search_fields = ("event_name",)