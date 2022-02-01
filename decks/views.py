from django.shortcuts import render,redirect
from django.conf import settings
from .models import Deck, DeckCard, DeckType
from cards.models import Card, Set, Type

import os, json, re

bad_set_types = ["promo","funny","archenemy","starter","memorabilia"]

def mobile(request):
    MOBILE_AGENT_RE = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)

    if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
        return True
    else:
        return False

# Create your views here.
def index(request):
    try:
        action = request.POST['action']
        if action != "reset":
            arr = json.loads(action)
            ids = []
            for i, val in enumerate(arr):
                try:
                    id = int(val)
                    ids.append(id)
                    dt = DeckType(pk=id)
                    dt.name = request.POST['name-{}'.format(id)]
                    dt.sort_order = i
                    dt.save()
                except ValueError:
                    dt = DeckType(name=val,sort_order=i)
                    dt.save()
                    ids.append(dt.id)
            to_delete = DeckType.objects.exclude(id__in=ids)
            for dt in to_delete:
                dt.delete()
    except KeyError:
        pass
    context = {"deck_types":DeckType.objects.all().order_by('sort_order','name')}
    if mobile(request):
        return render(request, 'decks/m_index.html', context)
    else:
        return render(request, 'decks/index.html', context)

def add(request):
    try:
        context = {"decks":Deck.objects.all().order_by('name'),"deck_types":DeckType.objects.all().order_by('sort_order','name')}
        name = request.POST['name'].strip()
        if len(name) > 0:
            d = Deck(name=name,notes=request.POST['notes'],deckType=DeckType.objects.get(pk=int(request.POST['deckType'])))
            d.save()
            if request.POST['inputType'] == "X":
                p = re.compile("(\\d+)x (.+)")
            else:
                p = re.compile("(\\d+) (.+)")
            issue_list = []
            cards = None
            if len(request.POST['list'].strip().replace('\r\n','\n')) != 0:
                main = request.POST['list'].strip().replace('\r\n','\n').split('\n')
            else:
                main = []
            if len(request.POST['sideboard'].strip().replace('\r\n','\n')) != 0:
                total = main + request.POST['sideboard'].strip().replace('\r\n','\n').split('\n')
            else:
                total = main
            for i,line in enumerate(total):
                m = p.match(line.strip())
                if m is None:
                    issue_list.append("Line {} is badly formed. Card could not be added.".format(line))
                else:
                    c = Card.objects.filter(name__iexact=m.groups()[1])
                    if len(c) == 0:
                        #try json
                        if cards is None:
                            f = open(os.path.join(settings.BASE_DIR, 'AtomicCards.json'),'r',encoding='utf8')
                            cards = json.load(f)["data"]
                            f.close()
                        if m.groups()[1] in cards:
                            c = Card(name=m.groups()[1],
                                text=cards[m.groups()[1]][0]['text'],
                                notes="",
                                addMana=False)
                            #mana cost
                            if "manaCost" in cards[m.groups()[1]][0]:
                                c.manaCost = cards[m.groups()[1]][0]['manaCost'].replace('}{',',').replace('{','').replace('}','').replace('/','')
                            #ptl
                            if "power" in cards[m.groups()[1]][0]:
                                c.power = cards[m.groups()[1]][0]["power"]
                            if "toughness" in cards[m.groups()[1]][0]:
                                c.toughness = cards[m.groups()[1]][0]["toughness"]
                            if "loyalty" in cards[m.groups()[1]][0]:
                                c.loyalty = cards[m.groups()[1]][0]["loyalty"]
                            c.save()
                            #types
                            if "supertypes" in cards[m.groups()[1]][0]:
                                for type in cards[m.groups()[1]][0]['supertypes']:
                                    t = Type.objects.filter(name__exact=type,typeType__exact=2)
                                    if len(t) == 0:
                                        t = Type(name=type,typeType=2)
                                        t.save()
                                    else:
                                        t = t[0]
                                    c.types.add(t)
                            if "types" in cards[m.groups()[1]][0]:
                                for type in cards[m.groups()[1]][0]['types']:
                                    t = Type.objects.filter(name__exact=type,typeType__exact=3)
                                    if len(t) == 0:
                                        t = Type(name=type,typeType=3)
                                        t.save()
                                    else:
                                        t = t[0]
                                    c.types.add(t)
                            if "subtypes" in cards[m.groups()[1]][0]:
                                for type in cards[m.groups()[1]][0]['subtypes']:
                                    t = Type.objects.filter(name__exact=type,typeType__exact=1)
                                    if len(t) == 0:
                                        t = Type(name=type,typeType=1)
                                        t.save()
                                    else:
                                        t = t[0]
                                    c.types.add(t)
                            #sets
                            f = open(os.path.join(settings.BASE_DIR, 'SetList.json'),'r',encoding='utf8')
                            sets = json.load(f)["data"]
                            f.close()
                            if "printings" in cards[m.groups()[1]][0]:
                                for code in cards[m.groups()[1]][0]["printings"]:
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
                            if i < len(main):
                                dc = DeckCard(card=c,count=int(m.groups()[0]),deck=d)
                            else:
                                dc = DeckCard(card=c,sideboard_count=int(m.groups()[0]),deck=d)
                            dc.save()
                        else:
                            issue_list.append("Could not find a card named {}. Card could not be added.".format(m.groups()[1]))
                    else:
                        if i < len(main):
                            dc = DeckCard(card=c[0],count=int(m.groups()[0]),deck=d)
                        else:
                            dc = DeckCard(card=c[0],sideboard_count=int(m.groups()[0]),deck=d)
                        dc.save()
            if len(issue_list) > 0:
                context['saved'] = '\\n'.join(issue_list)
                context['new_deck'] = d.id
            else:
                return redirect('/decks/{}'.format(d.id))
        else:
            context['error'] = "Deck must have a name."
        if mobile(request):
            return render(request, 'decks/m_add.html', context)
        else:
            return render(request, 'decks/add.html', context)
    except KeyError:
        if mobile(request):
            return render(request, 'decks/m_add.html', context)
        else:
            return render(request, 'decks/add.html', context)
    except OSError as ex:
        print(ex)

def detail(request, deck_id):
    context = None
    try:
        action = request.POST['action']
        if action == 'delete':
            Deck.objects.get(pk=deck_id).delete()
            return redirect('/decks/')
        elif action == 'update':
            d = Deck.objects.get(pk=deck_id)
            d.name = request.POST["name"]
            d.deckType = DeckType.objects.get(pk=int(request.POST['deckType']))
            d.notes = request.POST["notes"]
            d.save()
            for dc in d.deckcard_set.all():
                if 'count-{}'.format(dc.id) in request.POST:
                    dc.count = int(request.POST['count-{}'.format(dc.id)])
                if 'sideboard_count-{}'.format(dc.id) in request.POST:
                    dc.sideboard_count = int(request.POST['sideboard_count-{}'.format(dc.id)])
                if dc.count == 0 and dc.sideboard_count == 0:
                    dc.delete()
                else:
                    dc.save()
        elif action == 'ui':
            if "show_only_missing" in request.POST:
                context = {"show_only_missing":"show_only_missing"}
                request.session['show_only_missing'] = True
            else:
                request.session['show_only_missing'] = False
            if "show_extra" in request.POST:
                context = {"show_extra":"show_extra"}
                request.session['show_extra'] = True
            else:
                request.session['show_extra'] = False
        elif action == 'sets':
            f = open(os.path.join(settings.BASE_DIR, 'SetList.json'),'r',encoding='utf8')
            sets = json.load(f)["data"]
            f.close()
            f = open(os.path.join(settings.BASE_DIR, 'AtomicCards.json'),'r',encoding='utf8')
            cards = json.load(f)["data"]
            f.close()
            for dc in Deck.objects.get(pk=deck_id).deckcard_set.all():
                c = dc.card
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
        elif action == "search":
            context = {"card_name":request.POST["card_name"],"add_main_count":request.POST["add_main_count"],"add_side_count":request.POST["add_side_count"],"show_add":"show_add"}
            if request.POST["card_name"] != "":
                context["card_list"] = Card.objects.filter(name__startswith=request.POST["card_name"]).order_by('name')
        elif action.startswith("add"):
            if request.POST["add_main_count"] == "0" and request.POST["add_side_count"] == "0":
                context = {"card_name":request.POST["card_name"],
                    "add_main_count":request.POST["add_main_count"],
                    "add_side_count":request.POST["add_side_count"],
                    "add_err":"You must enter a value for either main or sideboard.",
                    "show_add":"show_add"}
                context["card_list"] = Card.objects.filter(name__startswith=request.POST["card_name"]).order_by('name')
            else:
                if "cards" in request.POST and request.POST["cards"] != "":
                    c = Card.objects.get(pk=request.POST["cards"])
                    dc = DeckCard.objects.filter(card=c,deck_id__exact=deck_id)
                    if len(dc) > 0:
                        context = {"card_name":request.POST["card_name"],
                            "add_main_count":request.POST["add_main_count"],
                            "add_side_count":request.POST["add_side_count"],
                            "add_err":"{} is already in the deck.".format(c.name),
                            "show_add":"show_add"}
                        context["card_list"] = Card.objects.filter(name__startswith=request.POST["card_name"]).order_by('name')
                    else:
                        dc = DeckCard(card=c,deck=Deck.objects.get(pk=deck_id),count=request.POST["add_main_count"],sideboard_count=request.POST["add_side_count"])
                        dc.save()
                        if action == "add_plus":
                            context = {"card_name":"",
                                "add_main_count":0,
                                "add_side_count":0,
                                "show_add":"show_add"}
                else:
                    context = {"card_name":request.POST["card_name"],
                        "add_main_count":request.POST["add_main_count"],
                        "add_side_count":request.POST["add_side_count"],
                        "add_err":"You must select a card.",
                        "show_add":"show_add"}
                    context["card_list"] = Card.objects.filter(name__startswith=request.POST["card_name"]).order_by('name')
        elif action.startswith("sort"):
            context = {"sort":int(action[4:])}
        if not action == "ui":
            if 'show_only_missing' in request.session:
                if request.session['show_only_missing']:
                    context = {"show_only_missing":"show_only_missing"}
            if 'show_extra' in request.session:
                if request.session['show_extra']:
                    context = {"show_extra":"show_extra"}
    except KeyError:
        if 'show_only_missing' in request.session:
            if request.session['show_only_missing']:
                context = {"show_only_missing":"show_only_missing"}
        if 'show_extra' in request.session:
            if request.session['show_extra']:
                context = {"show_extra":"show_extra"}
    if context is None:
        context = {"decks":Deck.objects.all().order_by('name'),"deck":Deck.objects.get(pk=deck_id)}
    else:
        context["decks"] = Deck.objects.all().order_by('name')
        context["deck"] = Deck.objects.get(pk=deck_id)
    if "sort" not in context:
        context["sort"] = 0
    context["deck_types"] = DeckType.objects.all().order_by('sort_order','name')
    if mobile(request):
        return render(request, 'decks/m_edit.html', context)
    else:
        return render(request, 'decks/edit.html', context)

def edit_card(request, deck_card_id):
    context = None
    try:
        action = request.POST['action']
        dc = DeckCard.objects.get(pk=deck_card_id)
        if action == 'save':
            dc.commander = "commander" in request.POST
            dc.count = int(request.POST['deck_count'])
            dc.sideboard_count = int(request.POST['sideboard_count'])
            if dc.count == 0 and dc.sideboard_count == 0:
                dc.delete()
            else:
                dc.save()
            c = dc.card
            c.count = int(request.POST['count'])
            c.addMana = 'add_mana' in request.POST
            c.notes = request.POST['notes']
            c.save()
        return redirect('/decks/{}'.format(dc.deck.id))
    except KeyError:
        context = {"deck_types":DeckType.objects.all().order_by('sort_order','name'),"deck_card":DeckCard.objects.get(pk=deck_card_id)}
        context["other_cards"] = DeckCard.objects.filter(card=context["deck_card"].card.id)
    
    if mobile(request):
        return render(request, 'decks/m_edit_card.html', context)
    else:
        return render(request, 'decks/edit_card.html', context)