# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from .views import login_view
# from .views import editeventform_view
# from .views import guestprofile_update, viewguestdetails_view, profile_view, superadmin
from django.contrib.auth.views import LogoutView
from . import views
from django.contrib import admin

# Forms
from .views import payee_form, import_students, fee_type_list, edit_fee_type, delete_fee_type, TransactionDeleteView, add_officer_view
from .views import remove_officer, StudentProfileView
from .views import StudentListView, OfficerListView, TransactionListView, TransactionRecentListView, Student_AccountView

urlpatterns = [

    path('login/', login_view, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),


    path('index/', StudentListView.as_view(), name='index'),
    path('dashboard-transaction/', TransactionListView.as_view(), name='dashboard_transaction'),
    path('list-transaction/', TransactionRecentListView.as_view(), name='list_transaction'),
    path('list-transaction/delete/<int:pk>/', TransactionDeleteView.as_view(), name='transaction-delete'),
    path('student/<str:student_number>/', views.student_detail_view, name='student_detail'),
    
    path('index-guest/', Student_AccountView, name='index_guest'),
    path('student-profile/', StudentProfileView.as_view(), name='student_profile'),

    path('officer-profile/', OfficerListView.as_view(), name='officer_profile'),
    path('officer/add/', add_officer_view, name='add-officer'),
    path('officer/remove/<int:officer_id>/', remove_officer, name='remove-officer'),

    path('transaction/payee/', payee_form, name="payee"),
    path('import-students/', import_students, name='import_students'),
    
    path('fee-types/', fee_type_list, name='fee_type_list'),
    path('fee-types/edit/<int:pk>/', edit_fee_type, name='edit_fee_type'),
    path('fee-types/delete/<int:pk>/', delete_fee_type, name='delete_fee_type'),
    
]

