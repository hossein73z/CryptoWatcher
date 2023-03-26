from django.urls import path

from . import views

urlpatterns = [
    path('', views.pair_list, name="pair_list"),
    path('new/', views.new_pair, name="new_pair"),
    path('add/', views.add_pair, name="add_pair"),
]
