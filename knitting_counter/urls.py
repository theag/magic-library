from django.urls import path

from . import views

app_name = "knitting_counter"

urlpatterns = [
    path('', views.index, name="index"),
    path('add', views.add, name="add"),
    path('<int:project_id>', views.use, name="use"),
    #path('<int:project_id>/edit', views.edit, name="edit"),
]