from django.http import HttpResponse
from django.shortcuts import render_to_response
import json
import itertools
import random
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
  maxi_similar = max([score[2] for score in similar_with_score])
  mini_similar = min([score[2] for score in similar_with_score])
  normalized = [(normalize_truth_score(assertion[1]), assertion[0], (assertion[2]-mini_similar)/(maxi_similar-mini_similar))
                for assertion in similar_with_score]
  return normalized

def similar_endpoint(request, left, relation, right, count, threshold):
  left = left.replace("_", " ")
  right = right.replace("_", " ")
  count = int(count)
  assertion = "%s %s %s" % (left, relation, right)
  try:
    # Filter first by seeing what's under the threshold, then look at our count
    similar_assertions = get_similar_assertions(left, relation, right)
    similar_assertions = list(itertools.takewhile(lambda x: x[0] > float(threshold)/100, similar_assertions))
    if len(similar_assertions) > count:
      # Keep the most and least true, and return a random sampling of the rest
      similar_assertions = [similar_assertions[0]] + \
                           [similar_assertions[1:-1][i] for i in sorted(random.sample(xrange(len(similar_assertions[1:-1])), count-3))] + \
                           [similar_assertions[-1]]
  except KeyError as e:
    return HttpResponse(json.dumps("!!%s" % str(e)))
  #return HttpResponse(json.dumps(similar_assertions))
  out = [{"id": assertion,
         "name": assertion,
         "data": {"$dim": 40 * normalize_truth_score(d4d.c4.how_true_is(assertion))},
         "adjacencies": [
          {"nodeTo": a[1],
           "data":
            {"$lineWidth": 10*a[2]+1}
          } for a in similar_assertions]}]
  out = out + [{"id": a[1],
                "name": a[1],
                "data": {"$dim": 40*a[0]},
                "adjacencies": {"nodeTo": assertion,
                                "data": {"$lineWidth": 10*a[2]+1}}
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
