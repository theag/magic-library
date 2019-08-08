from django.urls import path

from . import views

app_name = "decks"

urlpatterns = [
    path('', views.index, name="index"),
    path('add', views.add, name="add"),
    path('<int:deck_id>/', views.detail, name="deck"),
    path('cards/<int:deck_card_id>/', views.edit_card, name="edit_card"),
]