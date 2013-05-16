from django.http import HttpResponse
from django.shortcuts import render_to_response
import json
from d4d_visualize import d4dExplorer
from django.template import RequestContext
from d4d import d4d

# Create your views here.

explorer = d4dExplorer()

def get_similar_assertions(left, relation, right):
  similar_left = d4d.c4.similar_concepts_to(left)
  similar_right = d4d.c4.similar_concepts_to(right)
  similar_assertions = ["%s %s %s" % (str(left[0]), relation, str(right[0]))
                        for left in similar_left
                        for right in similar_right]
  similar_with_score = [(str(assertion), d4d.c4.how_true_is(str(assertion)))
                        for assertion in similar_assertions]
  similar_with_score.sort(key=lambda x: x[1], reverse=True)
  return similar_with_score

def similar_endpoint(request, left, relation, right, count):
  return HttpResponse(str(get_similar_assertions(left, relation, right)[:int(count)]))

def get_children(concept, exclude):
  explorer.concept = concept
  return [{"id": str(s[0]), "name": str(s[0]), "data": [], "children": []} for s in explorer.get_similar() if str(s[0]) not in exclude]
  

def visualize(request):
  return render_to_response('index.html', {},
         context_instance=RequestContext(request))

def index(request, query):
  query.replace("_", " ")
  explorer.concept = query
  similar = explorer.get_similar()
  out = {"id": query,
         "name": query,
         "data": [],
         "children": [{"id": str(s[0]), "name": str(s[0]), "data": [], "children": get_children(str(s[0]), query)} for s in similar]}
  return HttpResponse(json.dumps(out))
