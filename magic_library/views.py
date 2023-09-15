from django.shortcuts import render
import re
import xml.etree.ElementTree as ET

def mobile(request):
    MOBILE_AGENT_RE = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)

    if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
        return True
    else:
        return False

def index(request):
    if mobile(request):
        return render(request, 'magic_library/m_index.html')
    else:
        try:
            root = ET.fromstring(request.POST["xml"])
            deck_list = [[],[]]
            for child in root:
                if child.tag == "Cards":
                    if child.attrib["Sideboard"] == "true":
                        deck_list[1].append(child.attrib["Quantity"] +" " +child.attrib["Name"])
                    else:
                        deck_list[0].append(child.attrib["Quantity"] +" " +child.attrib["Name"])
            return render(request, 'magic_library/index.html',{"deck_list":deck_list})
        except KeyError:
            return render(request, 'magic_library/index.html')