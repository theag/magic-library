from django.db import models
from django import forms

# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=200)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Counter(models.Model):
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    count = models.SmallIntegerField(default=0)
    use_repeats = models.BooleanField(default=False)
    repeat_size = models.SmallIntegerField(default=0)
    repeat_count = models.SmallIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
        
    def dumps(self):
        return {'name':self.name,'count':self.count,'use_repeats':self.use_repeats,
            'repeat_size':self.repeat_size,'repeat_count':self.repeat_count}
    
    def loads(self, d):
        self.name = d['name']
        self.count = d['count']
        self.use_repeats = d['use_repeats']
        self.repeat_size = d['repeat_size']
        self.repeat_count = d['repeat_count']

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"

class CounterForm(forms.ModelForm):
    class Meta:
        model = Counter
        exclude = ['project']