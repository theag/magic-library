from django.shortcuts import render, redirect

from .models import Pattern,Floss,Stitch

import json,cross_stitch.dmc

# Create your views here.
def index(request):
    context = {'pattern_list': Pattern.objects.order_by('name')}
    return render(request,'cross_stitch/index.html',context)

def new(request):
    context = {'pattern':Pattern()}
    try:
        context['pattern'].name = request.POST['name']
        context['pattern'].width = request.POST['width']
        context['pattern'].height = request.POST['height']
        if context['pattern'].name == "":
            context['error'] = "Name cannot be empty."
        else:
            context['pattern'].save()
            floss = Floss(pattern=context['pattern'],
                colour_code='666',
                name='Bright Red',
                rgb=bytes.fromhex('E31D42'),
                order=1)
            floss.save()
            floss = Floss(pattern=context['pattern'],
                colour_code='307',
                name='Lemon',
                rgb=bytes.fromhex('FDED54'),
                order=2)
            floss.save()
            floss = Floss(pattern=context['pattern'],
                colour_code='906',
                name='Medium Parrot Green',
                rgb=bytes.fromhex('7FB335'),
                order=3)
            floss.save()
            floss = Floss(pattern=context['pattern'],
                colour_code='826',
                name='Medium Blue',
                rgb=bytes.fromhex('6B9EBF'),
                order=4)
            floss.save()
            floss = Floss(pattern=context['pattern'],
                colour_code='310',
                name='Black',
                rgb=bytes.fromhex('000000'),
                order=5)
            floss.save()
            floss = Floss(pattern=context['pattern'],
                colour_code='BLANC',
                name='White',
                rgb=bytes.fromhex('FFFFFF'),
                order=6)
            floss.save()
            return redirect('/edit',pattern_id=context['pattern'].id)
    except KeyError:
        pass
    return render(request, 'cross_stitch/new.html', context)

def edit(request, pattern_id):
    p = Pattern.objects.get(pk=pattern_id)
    context = {'pattern':p,'selected_floss':-1}
    try:
        p_arr = json.loads(request.POST['pattern_string'])
        context['selected_floss'] = int(request.POST['selected_floss'])
        for row in range(len(p_arr)):
            for col in range(len(p_arr[row])):
                curr = Stitch.objects.filter(pattern=p,row=row+1,column=col+1)
                if curr and p_arr[row][col] != curr[0].floss.id:
                    if p_arr[row][col] < 0:
                        curr[0].delete()
                        print("{} {} delete stitch".format(row+1,col+1))
                    else:
                        curr[0].floss = Floss.objects.get(id=p_arr[row][col])
                        curr[0].save()
                        print("{} {} update stitch".format(row+1,col+1))
                elif not curr and p_arr[row][col] >= 0:
                    print("{} {} make new stitch".format(row+1,col+1))
                    s = Stitch(pattern=p,floss=Floss.objects.get(id=p_arr[row][col]),row=row+1,column=col+1)
                    s.save()
                    
    except KeyError:
        pass
    print(context)
    return render(request, 'cross_stitch/edit.html', context)

def edit_floss(request, pattern_id):
    p = Pattern.objects.get(pk=pattern_id)
    context = {'pattern':p,'all_dmc':dmc.all_dmc}
    try:
        request.POST['action']
    except KeyError:
        pass
    return render(request,'cross_stitch/edit_floss.html',context)