from django.http import HttpResponse
from django.shortcuts import render_to_response
import json
from d4d_visualize import d4dExplorer
from django.template import RequestContext
from d4d import d4d

# Create your views here.

explorer = d4dExplorer()
mini = 0
maxi = 0

def normalize_truth_score(score):
  global maxi, mini
  if maxi == 0:
    maxi = 1
  return (score - mini) / (maxi - mini)

def get_similar_assertions(left, relation, right):
  similar_left = d4d.c4.similar_concepts_to(left)
  similar_right = d4d.c4.similar_concepts_to(right)
  similar_assertions = [("%s %s %s" % (str(left[0]), relation, str(right[0])),
                         left[1] * right[1])
                        for left in similar_left
                        for right in similar_right]
  # Rank and sort based on how "true" they are
  similar_with_score = [(str(assertion[0]), d4d.c4.how_true_is(str(assertion[0])), assertion[1])
                        for assertion in similar_assertions]
  similar_with_score.sort(key=lambda x: x[1], reverse=True)
  # Normalize before we return so we can use a 0-1 slider
  global maxi, mini
  maxi = max([score[1] for score in similar_with_score])
  mini = min([score[1] for score in similar_with_score])
  normalized = dict([(normalize_truth_score(assertion[1]), (assertion[0], assertion[2]))
                for assertion in similar_with_score])
  return normalized

def similar_endpoint(request, left, relation, right, count):
  left = left.replace("_", " ")
  right = right.replace("_", " ")
  assertion = "%s %s %s" % (left, relation, right)
  similar_assertions = get_similar_assertions(left, relation, right)[:int(count)]
  return HttpResponse(json.dumps(out))
  out = [{"id": assertion,
         "name": assertion,
         "data": {"$dim": 30 * normalize_truth_score(d4d.c4.how_true_is(assertion))},
         "adjacencies": [
          {"nodeTo": a[0],
           "data":
            {"$lineWidth": 16}
          } for a in similar_assertions]}]
  out = out + [{"id": a[0],
                "name": a[0],
                "data": {"$dim": 30*a[1]},
                "adjacencies": {"nodeTo": assertion,
                                "data": {"$lineWidth": 16}}
               } for a in similar_assertions]
  return HttpResponse(json.dumps(out))

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
