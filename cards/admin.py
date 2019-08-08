from django.contrib import admin

# Register your models here.
from .models import Type, Card, Set

admin.site.register(Card)
admin.site.register(Type)
admin.site.register(Set)