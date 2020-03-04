from django.db import models
from cards.models import Card,Type

TYPE_LIST = ["Creature","Instant","Sorcery","Enchantment","Artifact"]

class DeckType(models.Model):
    name = models.CharField(max_length=200)
    sort_order = models.SmallIntegerField(default=0)

    def sorted_decks(self):
        return self.deck_set.all().order_by("name")


class Deck(models.Model):
    name = models.CharField(max_length=200)
    deckType = models.ForeignKey(DeckType,on_delete=models.CASCADE)
    notes = models.TextField(blank=True)

    def deck_list(self):
        return self.deckcard_set.filter(count__gt=0).order_by('-commander','card__name')

    def sidebord(self):
        return self.deckcard_set.filter(sideboard_count__gt=0).order_by('card__name')

    def card_count(self):
        return self.deckcard_set.all().aggregate(models.Sum('count'))['count__sum']

    def mana_curve(self):
        rv = [0]
        for dc in self.deckcard_set.filter(count__gt=0):
            if dc.card.manaCost != "":
                ind = dc.card.cmc()
                while ind >= len(rv):
                    rv.append(0)
                rv[ind] += dc.count
        return rv

    def sideboard(self):
        return self.deckcard_set.filter(sideboard_count__gt=0).order_by('card__name')

    def sideboard_count(self):
        return self.deckcard_set.all().aggregate(models.Sum('sideboard_count'))['sideboard_count__sum']

    def deck_set_list(self):
        basic = Type.objects.filter(typeType=2,name__iexact="basic")[0]
        rv = {}
        for dc in self.deckcard_set.all():
            if dc.card.types.filter(pk=basic.id).exists():
                if "Basic Land" in rv:
                    rv["Basic Land"].append(dc)
                else:
                    rv["Basic Land"] = [dc]
            elif not dc.card.set_set.all().exists():
                if "No Set" in rv:
                    rv["No Set"].append(dc)
                else:
                    rv["No Set"] = [dc]
            else:
                for set in dc.card.set_set.all():
                    if set.name in rv:
                        rv[set.name].append(dc)
                    else:
                        rv[set.name] = [dc]
        return rv

    def card_colours(self):
        rv = {}
        for dc in self.deckcard_set.filter(count__gt=0):
            c = dc.card.colours()
            if c > 0:
                lbl = ""
                if c & 1 > 0:
                    lbl = "White"
                if c & 2 > 0:
                    if len(lbl) > 0:
                        lbl += "/"
                    lbl += "Blue"
                if c & 4 > 0:
                    if len(lbl) > 0:
                        lbl += "/"
                    lbl += "Black"
                if c & 8 > 0:
                    if len(lbl) > 0:
                        lbl += "/"
                    lbl += "Red"
                if c & 16 > 0:
                    if len(lbl) > 0:
                        lbl += "/"
                    lbl += "Green"
                if lbl in rv:
                    rv[lbl] += dc.count
                else:
                    rv[lbl] = dc.count
        return rv

    def card_dots(self):
        rv = {}
        for dc in self.deckcard_set.filter(count__gt=0):
            for m in dc.card.manaArr():
                if len(m) > 0:
                    lbl = ""
                    if m[0] == "W":
                        lbl = "White"
                    elif m[0] == "U":
                        lbl = "Blue"
                    elif m[0] == "B":
                        lbl = "Black"
                    elif m[0] == "R":
                        lbl = "Red"
                    elif m[0] == "G":
                        lbl = "Green"
                    if len(m) > 1 and m[1] != "P":
                        if m[1] == "W":
                            lbl += "/White"
                        elif m[1] == "U":
                            lbl += "/Blue"
                        elif m[1] == "B":
                            lbl += "/Black"
                        elif m[1] == "R":
                            lbl += "/Red"
                        elif m[1] == "G":
                            lbl += "/Green"
                    if len(lbl) > 0:
                        if lbl in rv:
                            rv[lbl] += dc.count
                        else:
                            rv[lbl] = dc.count
        return rv
    
    def types(self):
        rv = dict.fromkeys(TYPE_LIST, 0)
        for dc in self.deckcard_set.all():
            for t in dc.card.types.all():
                if t.name in rv:
                    rv[t.name] += 1
        return rv

    def land(self):
        rv = []
        land_type = Type.objects.filter(typeType=3,name__iexact="land")[0]
        for dc in self.deckcard_set.all().order_by("card__name"):
            if dc.card.types.filter(pk=land_type.id).exists():
                rv.append(dc)
        return rv

    def land_count(self):
        rv = 0
        land_type = Type.objects.filter(typeType=3,name__iexact="land")[0]
        for dc in self.deckcard_set.all().order_by("card__name"):
            if dc.card.types.filter(pk=land_type.id).exists():
                rv += dc.count
        return rv


class DeckCard(models.Model):
    card = models.ForeignKey(Card,on_delete=models.CASCADE)
    count = models.SmallIntegerField(default=0)
    deck = models.ForeignKey(Deck,on_delete=models.CASCADE)
    commander = models.BooleanField(default=False)
    sideboard_count = models.SmallIntegerField(default=0)
