from django.shortcuts import render, redirect
from .models import Project, Counter, ProjectForm, CounterForm
import json

def get_counters(arr):
    c = []
    for val in arr:
        co = Counter()
        co.loads(val)
        c.append(co)
    return c

def str_counters(arr):
    c = []
    for val in arr:
        c.append(val.dumps())
    return json.dumps(c)

# Create your views here.
def index(request):
    context = {'projects':Project.objects.all().order_by('last_updated')}
    return render(request, 'knitting_counter/index.html', context)

def add(request):
    context = {}
    if request.POST:
        context['form'] = ProjectForm(request.POST,prefix="project")
        counters = get_counters(json.loads(request.POST['counters']))
        action = request.POST['action']
        if action == 'change':
            if request.POST['counter_id'] == '-1':
                context['cform'] = CounterForm(prefix='counter')
                context['counter_id'] = -1
            elif request.POST['counter_id'] != "":
                context['counter_id'] = int(request.POST['counter_id'])
                context['cform'] = CounterForm(instance=counters[context['counter_id']],prefix='counter')
        elif action == 'counter':
            cf = CounterForm(request.POST,prefix='counter')
            if cf.is_valid():
                c = cf.save(commit=False)
                if request.POST['counter_id'] == '-1':
                    counters.append(c)
                elif request.POST['counter_id'] != "":
                    counters[int(request.POST['counter_id'])] = c
            else:
                context['cform'] = cf
                if request.POST['counter_id'] == '-1':
                    counters.append(c)
                elif request.POST['counter_id'] != "":
                    counters[int(request.POST['counter_id'])] = c
                context['counter_id'] = int(request.POST['counter_id'])
        elif action == "save":
            if context['form'].is_valid():
                p = context['form'].save()
                for c in counters:
                    c.project = p
                    c.save()
                return redirect('knitting_counter:use',p.id)
        context['counters'] = counters
        context['cstr'] = str_counters(counters)
    else:
        context['form'] = ProjectForm(prefix="project")
        context['cstr'] = '[]'
    return render(request, 'knitting_counter/add.html', context)

def use(request, project_id):
    context = {'project':Project.objects.get(pk=project_id)}
    context['current_counter'] = context['project'].counter_set.all()[0].id
    return render(request, 'knitting_counter/use.html', context)
    