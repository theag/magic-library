from django.urls import path

from . import views

app_name = 'cross_stitch'
urlpatterns = [
    path('',views.index,name='index'),
    path('new',views.new,name='new'),
    path('<int:pattern_id>', views.edit, name='edit'),
    path('<int:pattern_id>/floss', views.edit_floss, name='edit_floss'),
]