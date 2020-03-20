from django.urls import path

from . import views

app_name = "whiteboard"

urlpatterns = [
    path('', views.index, name="index"),
    path('add', views.add, name="add"),
    path('<int:whiteboard_id>', views.use, name="use"),
]