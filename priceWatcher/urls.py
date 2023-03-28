from django.urls import path

from . import views

urlpatterns = [
    path('', views.pair_list, name="pair_list"),
    path('add/', views.add_pair, name="add_pair"),
    path('adding/', views.kucoin_symbols, name="kucoin_symbols"),
    path("prices_json/", views.prices, name="prices_json"),
    path("delete/", views.delete_pair, name="delete_pair"),
]
