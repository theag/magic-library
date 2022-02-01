from django.db import models
import json

# Create your models here.
class Pattern(models.Model):
    name = models.CharField(max_length=50)
    width = models.IntegerField(default=100)
    height = models.IntegerField(default=100)
    
    def get_floss_json(self):
        f = {}
        for floss in self.floss_set.all():
            f[floss.id] = {"rgb":floss.rgb_hex_string(),"code":floss.colour_code}
        return json.dumps(f)
    
    def get_stitches(self):
        s = [[-1 for i in range(self.width)] for j in range(self.height)]
        for st in self.stitch_set.all():
            s[st.row-1][st.column-1] = st.floss.id
        return json.dumps(s)
        
    def canvas_width(self):
        return 100 +52*self.width;
    
    def canvas_height(self):
        return 100 +52*self.height;
        
    def get_ordered_floss(self):
        return self.floss_set.all().order_by('order')

class Floss(models.Model):
    pattern = models.ForeignKey(Pattern,on_delete=models.CASCADE)
    colour_code = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=1)
    rgb = models.BinaryField(max_length=3)
    order = models.PositiveIntegerField()
    
    def rgb_hex_string(self):
        return ''.join(format(x,'02x') for x in self.rgb)
    
class Stitch(models.Model):
    pattern = models.ForeignKey(Pattern,on_delete=models.CASCADE)
    floss = models.ForeignKey(Floss,on_delete=models.CASCADE)
    row = models.PositiveSmallIntegerField()
    column = models.PositiveSmallIntegerField()
    
    def __str__(self):
        return self.pattern.name +" " +self.floss.colour_code +" {} {}".format(self.row,self.column)