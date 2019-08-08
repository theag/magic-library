from django.db import models

# Create your models here.
class Type(models.Model):
    name = models.CharField(max_length=200)
    typeType = models.SmallIntegerField() # 1: sub, 2: super, 3: regular
    def __str__(self):
        if self.typeType == 1:
            return "Type: {} (sub)".format(self.name)
        elif self.typeType == 2:
            return "Type: {} (super)".format(self.name)
        elif self.typeType == 3:
            return "Type: {} (regular)".format(self.name)
    
class Set(models.Model):
    name = models.CharField(max_length=100)
    cards = models.ManyToManyField("Card")

class Card(models.Model):
    name = models.CharField(max_length=200)
    types = models.ManyToManyField(Type)
    manaCost = models.CharField(max_length=20,blank=True) # number or number X or colour single or colour P or colour colour
    text = models.TextField(blank=True)
    fancyText = models.TextField(blank=True)
    power = models.CharField(max_length=2,blank=True)
    toughness = models.CharField(max_length=2,blank=True)
    loyalty = models.CharField(max_length=2,blank=True)
    notes = models.TextField(blank=True)
    addMana = models.BooleanField()
    count = models.SmallIntegerField(default=0)
    lastUpdated = models.DateTimeField(auto_now=True)
    
    def cmc(self):
        if self.manaCost == '':
            return ''
        else:
            rv = 0
            for s in self.manaCost.split(','):
                try:
                    rv += int(s)
                except ValueError:
                    if len(s) == 1 or s[1] != 'X':
                        rv += 1
            return rv
    
    def manaArr(self):
        return self.manaCost.split(',')
    
    def super_types(self):
        rv = ""
        for st in self.types.filter(typeType__exact=2):
            if len(rv) > 0:
                rv = rv + " "
            rv = rv + st.name
        return rv
    
    def regular_types(self):
        rv = ""
        for st in self.types.filter(typeType__exact=3):
            if len(rv) > 0:
                rv = rv + " "
            rv = rv + st.name
        return rv
    
    def sub_types(self):
        rv = ""
        for st in self.types.filter(typeType__exact=1):
            if len(rv) > 0:
                rv = rv + " "
            rv = rv + st.name
        return rv
    
    def plt(self):
        if len(self.loyalty) > 0:
            return self.loyalty
        elif len(self.power) > 0:
            return self.power + "/" +self.toughness
        else:
            return ""
    
    def colours(self):
        rv = 0
        for m in self.manaArr():
            if "W" in m:
                rv = rv | 1
            if "U" in m:
                rv = rv | 2
            if "B" in m:
                rv = rv | 4
            if "R" in m:
                rv = rv | 8
            if "G" in m:
                rv = rv | 16
        return rv
    
    def print_sets(self):
        rv = ""
        for s in self.set_set.all():
            if len(rv) > 0:
                rv = rv + ", "
            rv = rv + s.name
        return rv
    
    def html_text(self):
        return self.text.replace("\n","<br/>").replace("\r","")
    
    def js_text(self):
        return self.text.replace("\n","\\n").replace("\r","").replace('"',"&quot;")