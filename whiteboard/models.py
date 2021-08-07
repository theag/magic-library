from django.db import models
from django import forms
from django.core.validators import MinValueValidator

class Whiteboard(models.Model):
    name = models.CharField(max_length=200)
    width = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    height = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    password = models.CharField(max_length=20)
    
    def create_pixels(self):
        for x in range(self.width):
            for y in range(self.height):
                p = Pixel(board=self,x=x,y=y)
                p.save()

class WhiteboardForm(forms.ModelForm):
    class Meta:
        model = Whiteboard
        fields = "__all__"
        widgets = {'password': forms.PasswordInput()}

class Pixel(models.Model):
    board = models.ForeignKey(Whiteboard,on_delete=models.CASCADE)
    x = models.PositiveSmallIntegerField()
    y = models.PositiveSmallIntegerField()
    colour = models.CharField(max_length=6,default="FFFFFF")
    last_changed = models.DateTimeField(auto_now=True)