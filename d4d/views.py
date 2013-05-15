from django.http import HttpResponse
from django.shortcuts import render_to_response
import json
from d4d_visualize import d4dExplorer
from django.template import RequestContext

# Create your views here.

explorer = d4dExplorer()

def get_children(concept, exclude):
  explorer.concept = concept
  return [{"id": str(s[0]), "name": str(s[0]), "data": [], "children": []} for s in explorer.get_similar() if str(s[0]) not in exclude]
  

def visualize(request):
  return render_to_response('index.html', {},
         context_instance=RequestContext(request))

def index(request, query):
  explorer.concept = query
  similar = explorer.get_similar()
  out = {"id": query,
         "name": query,
         "data": [],
         "children": [{"id": str(s[0]), "name": str(s[0]), "data": [], "children": get_children(str(s[0]), query)} for s in similar]}
  return HttpResponse(json.dumps(out))
