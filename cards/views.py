from django.shortcuts import render,redirect
from .models import Card,Type,Set
from decks.models import Deck,DeckCard
import os, json

bad_set_types = ["promo","funny","archenemy","starter","memorabilia"]

class AdvancedSearch:
    allAnd = True
    colourAnd = True
    colourless = False
    colourMask = 0
    superAnd = True
    supers = []
    typeAnd = True
    types = []
    cmc = []
    textAnd = True
    text = []
    noDeck = False
    decks = []
    notesAnd = True
    notes = []
    noNotes = False
    countOperator = 0 #<,<=,=,>=,>
    countNumber = 0
    addsMana = False
    setsAnd = True
    sets = []
    noSets = False
    
    def matches(self, card):
        results = []
        #colour
        if (not self.colourless) and self.colourMask == 0:
            pass
        elif self.colourAnd:
            #anding
            if self.colourless:
                if self.colourMask != 0:
                    #can't be coloured and colourless
                    results.append(False)
                else:
                    #checking if colourless
                    if card.colours() != 0:
                        results.append(False)
                    else:
                        results.append(True)
            else:
                #checking for colour
                results.append(self.colourMask == card.colours())
        else:
            #oring
            results.append((self.colourMask & card.colours()) != 0 or (self.colourless and card.colours() == 0))
        #supers
        if self.superAnd:
            results.append(True)
            for t in self.supers:
                if len(card.types.filter(id=t)) == 0:
                    results[-1] = False
                    break
        else:
            results.append(False)
            for t in self.supers:
                if len(card.types.filter(id=t)) > 0:
                    results[-1] = True
                    break
        #types
        if self.typeAnd:
            results.append(True)
            for t in self.types:
                if len(card.types.filter(id=t)) == 0:
                    results[-1] = False
                    break
        else:
            results.append(False)
            for t in self.types:
                if len(card.types.filter(id=t)) > 0:
                    results[-1] = True
                    break
        #cmc
        if len(self.cmc) > 0:
            results.append(card.cmc() in self.cmc)
        #text
        if len(self.text) > 0:
            if len(card.text) == 0:
                results.append(False)
            elif self.textAnd:
                results.append(True)
                for t in self.text:
                    if t.lower() not in card.text.lower():
                        results[-1] = False
                        break
            else:
                results.append(False)
                for t in self.text:
                    if t.lower() in card.text.lower():
                        results[-1] = True
                        break
        #decks
        if self.noDeck:
            results.append(len(card.deckcard_set.all()) == 0)
        elif len(self.decks) > 0:
            results.append(False)
            for d in self.decks:
                if card.deckcard_set.filter(deck__name__iexact=d).exists():
                    results[-1] = True
                    break
        #notes
        if len(self.notes) > 0:
            if len(card.notes) == 0:
                results.append(False)
            elif self.notesAnd:
                results.append(True)
                for t in self.notes:
                    if t.lower() not in card.notes.lower():
                        results[-1] = False
                        break
            else:
                results.append(False)
                for t in self.notes:
                    if t.lower() in card.notes.lower():
                        results[-1] = True
                        break
        #card count
        if self.countOperator == 0:
            results.append(card.count < self.countNumber)
        elif self.countOperator == 1:
            results.append(card.count <= self.countNumber)
        elif self.countOperator == 2:
            results.append(card.count == self.countNumber)
        elif self.countOperator == 3:
            results.append(card.count >= self.countNumber)
        elif self.countOperator == 4:
            results.append(card.count > self.countNumber)
        #adds mana
        if self.addsMana:
            results.append(card.addMana)
        #sets
        if self.noSets:
            results.append(len(card.set_set.all()) == 0)
        elif len(self.sets) > 0:
            if self.setsAnd:
                results.append(True)
                for t in self.sets:
                    if len(card.set_set.filter(name__iexact=t)) == 0:
                        results[-1] = False
                        break
            else:
                results.append(False)
                for t in self.sets:
                    if len(card.set_set.filter(name__iexact=t)) > 0:
                        results[-1] = True
                        break
        #results
        rv = self.allAnd
        if self.allAnd:
            for r in results:
                rv = rv and r
        else:
            for r in results:
                rv = rv or r
        return rv

# Create your views here.
def index(request):
    context = None
    try:
        action = request.POST['action']
        if action == "search" and len(request.POST["simple_search"]) > 0:
            context = {"search_results":Card.objects.filter(name__startswith=request.POST["simple_search"]).order_by('name'),"simple_search":request.POST["simple_search"]}
        elif action == "switcha" or action == "advanced":
            context = {"isadvanced":"isadvanced","supers":Type.objects.filter(typeType=2).order_by('name'),
                "types":Type.objects.filter(typeType=3).order_by('name'),"countOperator":3,"countNumber":0,"deck_list":Deck.objects.all().order_by("name")}
            if action == "advanced":
                avs = AdvancedSearch()
                avs.allAnd = "andAll" not in request.POST.keys()
                if not avs.allAnd:
                    context["andAll"] = "andAll"
                #Colour
                avs.colourAnd = "andColour" not in request.POST.keys()
                if not avs.colourAnd:
                    context["andColour"] = "andColour"
                avs.colourless = "colourless" in request.POST.keys()
                if avs.colourless:
                    context["colourless"] = "colourless"
                if "white" in request.POST.keys():
                    avs.colourMask = avs.colourMask | 1
                    context["white"] = "white"
                if "blue" in request.POST.keys():
                    avs.colourMask = avs.colourMask | 2
                    context["blue"] = "blue"
                if "black" in request.POST.keys():
                    avs.colourMask = avs.colourMask | 4
                    context["black"] = "black"
                if "red" in request.POST.keys():
                    avs.colourMask = avs.colourMask | 8
                    context["red"] = "red"
                if "green" in request.POST.keys():
                    avs.colourMask = avs.colourMask | 16
                    context["green"] = "green"
                #supers and types
                avs.superAnd = "andSuper" not in request.POST.keys()
                if not avs.superAnd:
                    context["andSuper"] = "andSuper"
                context["typeChecked"] = []
                avs.typeAnd = "andType" not in request.POST.keys()
                if not avs.typeAnd:
                    context["andType"] = "andType"
                context["superChecked"] = []
                for k in request.POST.keys():
                    if k.startswith("type-"):
                        context["typeChecked"].append(int(k[5:]))
                        avs.types.append(int(k[5:]))
                    elif k.startswith("super-"):
                        context["superChecked"].append(int(k[6:]))
                        avs.supers.append(int(k[6:]))
                #cmc
                context["cmc"] = request.POST["cmc"]
                if len(context["cmc"]) > 0:
                    for c in context["cmc"].split(","):
                        avs.cmc.append(int(c))
                #text
                avs.textAnd = "andText" not in request.POST.keys()
                if not avs.textAnd:
                    context["andText"] = "andText"
                context["text"] = request.POST["text"]
                if len(context["text"]) > 0:
                    avs.text = context["text"].split(os.linesep)
                #decks
                avs.noDeck = "nodeck" in request.POST
                if avs.noDeck:
                    context["nodeck"] = "nodeck"
                context["decks"] = request.POST["decks"]
                if len(context["decks"]) > 0:
                    for d in context["decks"].split(","):
                        avs.decks.append(d)
                #notes
                avs.notesAnd = "andNotes" not in request.POST.keys()
                if not avs.notesAnd:
                    context["andNotes"] = "andNotes"
                context["notes"] = request.POST["notes"]
                if len(context["notes"]) > 0:
                    avs.notes = context["notes"].split(os.linesep)
                #card count
                avs.countOperator = int(request.POST["countOperator"])
                context["countOperator"] = avs.countOperator
                avs.countNumber = int(request.POST["countNumber"])
                context["countNumber"] = avs.countNumber
                #adds mana
                avs.addsMana = "addsMana" in request.POST.keys()
                if avs.addsMana:
                    context["addsMana"] = "addsMana"
                #sets
                avs.setsAnd = "andSets" not in request.POST.keys()
                if not avs.setsAnd:
                    context["andSets"] = "andSets"
                avs.noSets = "nosets" in request.POST.keys()
                if avs.noSets:
                    context["nosets"] = "nosets"
                context["sets"] = request.POST["sets"]
                if len(context["sets"]) > 0:
                    for c in context["sets"].split(","):
                        avs.sets.append(c)
                #search
                context["search_results"] = []
                for card in Card.objects.all().order_by('name'):
                    if avs.matches(card):
                        context["search_results"].append(card)
        else:
            context = {"search_results":Card.objects.all().order_by('name')}
    except KeyError:
        print("key error")
        context = {"search_results":Card.objects.all().order_by('name')}
    return render(request, 'cards/index.html', context)

def add(request):
    c = Card(manaCost="")
    context = {'mode':'add'}
    try:
        action = request.POST['action']
        c.name = request.POST['name']
        c.manaCost = request.POST['manaCost']
        c.text = request.POST['text']
        if request.POST['plt'] == "":
            c.power = ""
            c.toughness = ""
            c.loyalty = ""
        elif '/' in request.POST['plt']:
            ind = request.POST['plt'].index('/')
            c.power = request.POST['plt'][0:ind]
            c.toughness = request.POST['plt'][ind+1:]
            c.loyalty = ""
        else:
            c.power = ""
            c.toughness = ""
            c.loyalty = request.POST['plt']
        c.count = request.POST['count']
        c.addMana = 'add_mana' in request.POST
        c.notes = request.POST['notes']
        if action == "add":
            errors = []
            if c.name == "":
                errors.append("Name cannot be empty")
            if request.POST['regular_type'] == "":
                errors.append("Type cannot be empty")
            if len(errors) > 0:
                context['errors'] = errors
            else:
                c.save()
                if len(request.POST['super_type']) > 0:
                    for type in request.POST['super_type'].split(" "):
                        t = Type.objects.filter(name__exact=type,typeType__exact=2)
                        if len(t) == 0:
                            t = Type(name=type,typeType=2)
                            t.save()
                        else:
                            t = t[0]
                        c.types.add(t)
                if len(request.POST['regular_type']) > 0:
                    for type in request.POST['regular_type'].split(" "):
                        t = Type.objects.filter(name__exact=type,typeType__exact=3)
                        if len(t) == 0:
                            t = Type(name=type,typeType=3)
                            t.save()
                        else:
                            t = t[0]
                        c.types.add(t)
                if len(request.POST['sub_type']) > 0:
                    for type in request.POST['sub_type'].split(" "):
                        t = Type.objects.filter(name__exact=type,typeType__exact=1)
                        if len(t) == 0:
                            t = Type(name=type,typeType=1)
                            t.save()
                        else:
                            t = t[0]
                        c.types.add(t)
                return redirect('/cards/')
        context['super_type'] = request.POST['super_type']
        context['regular_type'] = request.POST['regular_type']
        context['sub_type'] = request.POST['sub_type']
    except KeyError as detail:
        print("key error: {}".format(detail))
        pass
    context['card'] = c
    return render(request, 'cards/edit.html', context)

def edit(request, card_id):
    c = Card.objects.get(pk=card_id)
    context = {'mode':'edit','all_decks':Deck.objects.all().order_by('name')}
    try:
        action = request.POST['action']
        c.name = request.POST['name']
        c.manaCost = request.POST['manaCost']
        c.text = request.POST['text']
        if request.POST['plt'] == "":
            c.power = ""
            c.toughness = ""
            c.loyalty = ""
        elif '/' in request.POST['plt']:
            ind = request.POST['plt'].index('/')
            c.power = request.POST['plt'][0:ind]
            c.toughness = request.POST['plt'][ind+1:]
            c.loyalty = ""
        else:
            c.power = ""
            c.toughness = ""
            c.loyalty = request.POST['plt']
        c.count = request.POST['count']
        c.addMana = 'add_mana' in request.POST
        c.notes = request.POST['notes']
        if action == "edit":
            errors = []
            if c.name == "":
                errors.append("Name cannot be empty")
            if request.POST['regular_type'] == "":
                errors.append("Type cannot be empty")
            if len(errors) > 0:
                context['errors'] = errors
            else:
                c.types.clear()
                c.save()
                if len(request.POST['super_type']) > 0:
                    for type in request.POST['super_type'].split(" "):
                        t = Type.objects.filter(name__exact=type,typeType__exact=2)
                        if len(t) == 0:
                            t = Type(name=type,typeType=2)
                            t.save()
                        else:
                            t = t[0]
                        c.types.add(t)
                if len(request.POST['regular_type']) > 0:
                    for type in request.POST['regular_type'].split(" "):
                        t = Type.objects.filter(name__exact=type,typeType__exact=3)
                        if len(t) == 0:
                            t = Type(name=type,typeType=3)
                            t.save()
                        else:
                            t = t[0]
                        c.types.add(t)
                if len(request.POST['sub_type']) > 0:
                    for type in request.POST['sub_type'].split(" "):
                        t = Type.objects.filter(name__exact=type,typeType__exact=1)
                        if len(t) == 0:
                            t = Type(name=type,typeType=1)
                            t.save()
                        else:
                            t = t[0]
                        c.types.add(t)
        elif action == "sets":
            f = open('SetList.json','r')
            sets = json.load(f)
            f.close()
            f = open('AllCards.json','r',encoding='utf8')
            cards = json.load(f)
            f.close()
            if c.name in cards:
                jc = cards[c.name]
                c.set_set.clear()
                if "printings" in jc:
                    for code in jc["printings"]:
                        for jset in sets:
                            if jset["code"] == code:
                                if jset["type"] not in bad_set_types:
                                    set = Set.objects.filter(name__exact=jset["name"])
                                    if len(set) == 0:
                                        set = Set(name=jset["name"])
                                        set.save()
                                    else:
                                        set = set[0]
                                    set.cards.add(c)
                                break

            else:
                context['errors'] = ["Can't find card with name '{}'".format(c.name)]
        elif action == "delete":
            c.delete()
            return redirect('/cards/')
        elif action == "remove":
            DeckCard.objects.get(pk=int(request.POST['deck'])).delete()
        elif action == "deckadd":
            dc = DeckCard(card=c,deck=Deck.objects.get(pk=int(request.POST['newdeck'])),count=int(request.POST['deck_count']))
            dc.commander = 'commander' in request.POST
            dc.sideboard_count = request.POST['sideboard_count']
            dc.save()
        context['super_type'] = request.POST['super_type']
        context['regular_type'] = request.POST['regular_type']
        context['sub_type'] = request.POST['sub_type']
    except KeyError as detail:
        print("key error: {}".format(detail))
    context['card'] = c
    context['decks'] = DeckCard.objects.filter(card=c).order_by('deck__name')
    return render(request, 'cards/edit.html', context)

def add_json(request):
    context = {"decks":Deck.objects.all().order_by("name")}
    try:
        action = request.POST['action']
        f = open('AllCards.json','r',encoding='utf8')
        cards = json.load(f)
        f.close()
        if action == "search":
            print(request.POST.getlist('deck_choices'))
            context = {"results":[],"name":request.POST["name"],"notes":request.POST["notes"],"decks":Deck.objects.all().order_by("name"),"deck_choices":map(int,request.POST.getlist('deck_choices'))}
            for name in cards.keys():
                if name.lower().startswith(request.POST["name"].lower()):
                    context["results"].append(name)
        elif action == "add" or action == "addp":
            for name in request.POST.getlist('cards'):
                c = Card(name=name,
                    text=cards[name]['text'],
                    notes=request.POST['notes'],
                    addMana=False)
                #mana cost
                if "manaCost" in cards[name]:
                    c.manaCost = cards[name]['manaCost'].replace('}{',',').replace('{','').replace('}','').replace('/','')
                #ptl
                if "power" in cards[name]:
                    c.power = cards[name]["power"]
                if "toughness" in cards[name]:
                    c.toughness = cards[name]["toughness"]
                if "loyalty" in cards[name]:
                    c.loyalty = cards[name]["loyalty"]
                c.save()
                #types
                if "supertypes" in cards[name]:
                    for type in cards[name]['supertypes']:
                        t = Type.objects.filter(name__exact=type,typeType__exact=2)
                        if len(t) == 0:
                            t = Type(name=type,typeType=2)
                            t.save()
                        else:
                            t = t[0]
                        c.types.add(t)
                if "types" in cards[name]:
                    for type in cards[name]['types']:
                        t = Type.objects.filter(name__exact=type,typeType__exact=3)
                        if len(t) == 0:
                            t = Type(name=type,typeType=3)
                            t.save()
                        else:
                            t = t[0]
                        c.types.add(t)
                if "subtypes" in cards[name]:
                    for type in cards[name]['subtypes']:
                        t = Type.objects.filter(name__exact=type,typeType__exact=1)
                        if len(t) == 0:
                            t = Type(name=type,typeType=1)
                            t.save()
                        else:
                            t = t[0]
                        c.types.add(t)
                #sets
                f = open('SetList.json','r')
                sets = json.load(f)
                f.close()
                if "printings" in cards[name]:
                    for code in cards[name]["printings"]:
                        for jset in sets:
                            if jset["code"] == code:
                                if jset["type"] not in bad_set_types:
                                    set = Set.objects.filter(name__exact=jset["name"])
                                    if len(set) == 0:
                                        set = Set(name=jset["name"])
                                        set.save()
                                    else:
                                        set = set[0]
                                    set.cards.add(c)
                                break
                #decks
                for d_id in request.POST.getlist('deck_choices'):
                    dc = DeckCard(card=c,count=1,deck=Deck.objects.get(pk=int(d_id)))
                    dc.save()
            if action == "add":
                return redirect('/cards/')
            else:
                context = {"results":[],"notes":request.POST["notes"],"decks":Deck.objects.all().order_by("name"),"deck_choices":map(int,request.POST.getlist('deck_choices'))}
    except KeyError as detail:
        print("key error: {}".format(detail))
        
    return render(request, 'cards/add_json.html', context)