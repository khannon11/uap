"""
Used to visualize ConceptNet with the aid of d4d
"""

import itertools
import os
import sys

class RedirectStdStreams(object):
  """ Avoid print statements from imported methods """
  def __init__(self, stdout=None, stderr=None):
    self._stdout = stdout or sys.stdout
    self._stderr = stderr or sys.stderr

  def __enter__(self):
    self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
    self.old_stdout.flush()
    self.old_stderr.flush()
    sys.stdout, sys.stderr = self._stdout, self._stderr

  def __exit__(self, exc_type, exc_value, traceback):
    self._stdout.flush()
    self._stderr.flush()
    sys.stdout = self.old_stdout
    sys.stderr = self.old_stderr

devnull = open(os.devnull, 'w')
with RedirectStdStreams(stdout=devnull, stderr=devnull):
  from d4d import d4d

class d4dExplorer:
  """
  Used to navigate ConceptNet
  e = d4dExplorer()
  e.run()
  """
  def __init__(self):
    self.concept = ''
    self.reset()

  def get_similar(self):
    """
    Get concepts that are similar to our current concept
    """
    if self.threshold is None:
      return d4d.c4.similar_concepts_to(self.concept, self.end)[self.start:]
    else:
      self.start = 0
      return list(itertools.takewhile(lambda x: x[1] > self.threshold,
                                d4d.c4.similar_concepts_to(self.concept, 1000)))

  def get_assertions(self):
    """
    Get any assertions related to our current concept
    """
    return d4d.c4.assertions_about(self.concept, 'both', self.end)[self.start:]

  def get_normalized_assertions(self):
    return [d4d.abnormalize_assertion(assertion) for assertion in
            self.get_assertions()]

  def print_similar(self):
    concepts = self.get_similar()

    print "\nConcept\t\tScore"
    print "-" * 27
    for concept in concepts:
      if concept[0] != self.concept:
        if len(concept[0]) > 7:
          print "%s\t%f" % (concept[0], concept[1])
        else:
          print "%s\t\t%f" % (concept[0], concept[1])
    print ""

  def reset(self):
    self.start = 0
    self.end = 10
    self.offset = 10
    self.threshold = None
    self.finish = False

  def run(self):
    """
    Loop to explore conceptnet from command line
    """
    self.finish = False
    while not self.finish:
      self.run_once()
    print "Thanks for playing!"

  def run_once(self):
    command_list = raw_input("What do you want to do? ").lower().split()
    command = command_list[0]

    if command == "similar":
      self.similar_to(command_list[1])

    elif command == "alter":
      self.alter(command_list[1], int(command_list[2]))

    elif command == "more":
      self.more()

    elif command == "exit" or command == "quit":
      self.finish = True

  def similar_to(self, concept = None):
    if concept is not None:
      self.concept = concept
    self.reset()
    self.print_similar()

  def setNumResults(self, num):
    self.threshold = None
    self.offset = num
    self.end = self.start + self.offset

  def alter(self, param, value):
    if param == "number":
      self.setNumResults(value)
      if self.concept:
        self.print_similar()
      else:
        print "Number of results altered"
    elif param == "threshold":
      self.threshold = value
      self.print_similar()

  def more(self):
    self.threshold = None
    self.start = self.end
    self.end = self.start + self.offset
    self.print_similar()

  def assertions(self, concept):
    pass
