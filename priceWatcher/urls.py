from django.urls import path

from . import views

urlpatterns = [
    path('', views.pair_list, name="pair_list")
]
