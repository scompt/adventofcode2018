#!/usr/bin/env python3

import sys
from textwrap import dedent
from itertools import product, chain, islice, zip_longest, count
import heapq
from io import StringIO
from collections import defaultdict, namedtuple
import os.path
import math
import types
from operator import attrgetter

class Nanobot:
  def __init__(self, x, y, z, strength):
    self.x = x
    self.y = y
    self.z = z
    self.strength = strength
  
  def distance_to(self, other):
    """
    >>> n1 = Nanobot(1,2,3,4)
    >>> n2 = Nanobot(2,3,4,5)
    >>> n1.distance_to(n1)
    0
    >>> n1.distance_to(n2)
    3
    """
    return abs(self.x-other.x) + abs(self.y-other.y) + abs(self.z-other.z)
  
  def __repr__(self):
    """
    >>> n = Nanobot(1,2,3,4)
    >>> n
    (1, 2, 3, 4)
    """
    return str((self.x, self.y, self.z, self.strength))
    
def parse(stream):
  """
  >>> inp = r'''
  ... pos=<0,0,0>, r=4
  ... pos=<1,0,0>, r=1
  ... pos=<4,0,0>, r=3
  ... pos=<0,2,0>, r=1
  ... pos=<0,5,0>, r=3
  ... pos=<0,0,3>, r=1
  ... pos=<1,1,1>, r=1
  ... pos=<1,1,2>, r=1
  ... pos=<1,3,1>, r=1
  ... '''
  >>> m = parse(StringIO(dedent(inp).strip()))
  >>> m
  [(0, 0, 0, 4), (1, 0, 0, 1), (4, 0, 0, 3), (0, 2, 0, 1), (0, 5, 0, 3), (0, 0, 3, 1), (1, 1, 1, 1), (1, 1, 2, 1), (1, 3, 1, 1)]
  """
  nanobots = []
  for l in stream.readlines():
    part = l[5:].partition(',')
    x = int(part[0])
    
    part = part[2].partition(',')
    y = int(part[0])

    part = part[2].partition('>, r=')
    z = int(part[0])

    strength = int(part[2])
    
    nanobots.append(Nanobot(x, y, z, strength))
  return nanobots

def strongest(nanobots):
  """
  >>> nanobots = [Nanobot(0, 0, 0, 4), Nanobot(1, 0, 0, 1), Nanobot(4, 0, 0, 3), Nanobot(0, 2, 0, 1), Nanobot(0, 5, 0, 3), Nanobot(0, 0, 3, 1), Nanobot(1, 1, 1, 1), Nanobot(1, 1, 2, 1), Nanobot(1, 3, 1, 1)]
  >>> strongest(nanobots)
  (0, 0, 0, 4)
  """
  return max(nanobots, key=attrgetter('strength'))

def in_range(center_bot, nanobots):
  """
  >>> nanobots = [Nanobot(0, 0, 0, 4), Nanobot(1, 0, 0, 1), Nanobot(4, 0, 0, 3), Nanobot(0, 2, 0, 1), Nanobot(0, 5, 0, 3), Nanobot(0, 0, 3, 1), Nanobot(1, 1, 1, 1), Nanobot(1, 1, 2, 1), Nanobot(1, 3, 1, 1)]
  >>> r = in_range(Nanobot(0, 0, 0, 4), nanobots)
  >>> r
  [(0, 0, 0, 4), (1, 0, 0, 1), (4, 0, 0, 3), (0, 2, 0, 1), (0, 0, 3, 1), (1, 1, 1, 1), (1, 1, 2, 1)]
  """
  return [b for b in nanobots if center_bot.distance_to(b) <= center_bot.strength]

def gogogo(stream):
  """
  >>> inp = r'''
  ... pos=<0,0,0>, r=4
  ... pos=<1,0,0>, r=1
  ... pos=<4,0,0>, r=3
  ... pos=<0,2,0>, r=1
  ... pos=<0,5,0>, r=3
  ... pos=<0,0,3>, r=1
  ... pos=<1,1,1>, r=1
  ... pos=<1,1,2>, r=1
  ... pos=<1,3,1>, r=1
  ... '''
  >>> go(parse(StringIO(dedent(inp).strip()))inp)
  7
  """
  nanobots = parse(stream)
  asdf = strongest(nanobots)
  closest = in_range(asdf, nanobots)
  return len(closest)

if len(sys.argv) == 2 and os.path.isfile(sys.argv[1]):
  print(gogogo(open(sys.argv[1])))

else:
  import doctest
  doctest.testmod(verbose=True)
