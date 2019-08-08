from django.urls import path

from . import views

app_name = "cards"

urlpatterns = [
    path('', views.index, name="index"),
    path('add', views.add, name="add"),
    path('<int:card_id>/', views.edit, name="edit"),
    path('add_json', views.add_json, name="json"),
]