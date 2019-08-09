from django.shortcuts import render
import re

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
        return render(request, 'magic_library/index.html')