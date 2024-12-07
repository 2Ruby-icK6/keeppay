# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views
from django.conf import settings

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    # path('1styearb1/', views.StudentListView, name="1styearb1"),


    # # Matches any html file
    # re_path(r'^.*\.*', views.pages, name='pages'),
]
