from django.shortcuts import render, redirect
from .models import Whiteboard, Pixel, WhiteboardForm
from django.forms.utils import ErrorList

# Create your views here.
def index(request):
    context = {'boards':Whiteboard.objects.all()}
    return render(request,'whiteboard/index.html',context)

def add(request):
    context = {}
    if request.POST:
        f = WhiteboardForm(request.POST)
        context['form'] = f
        if f.is_valid:
            if request.POST['password'] != request.POST['password_confirm']:
                f.add_error("password","Passwords do not match.")
            else:
                w = f.save()
                w.create_pixels()
                return redirect('whiteboard:index')
    else:
        context['form'] = WhiteboardForm()
    return render(request,'whiteboard/add.html',context)

def use(request,whiteboard_id):
    context = {'board':Whiteboard.objects.get(pk=whiteboard_id)}
    
    return render(request,'whiteboard/use.html',context)