#!/usr/bin/env python3

import sys
import os.path
from io import StringIO
from collections import defaultdict

sys.setrecursionlimit(15000)
#  too high 5137

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    pass

class State(object):
  def __init__(self):
    self.neighbors = []
  
  def __str__(self):
    return ''
  
  def __len__(self):
    return 0
  
class InitialState(State):
  def __init__(self):
    super(InitialState, self).__init__()

  def __str__(self):
    return '^'
  
  def __repr__(self):
    return 'InitialState()'
  
class FinalState(State):
  def __init__(self):
    super(FinalState, self).__init__()

  def __str__(self):
    return '$'
  
  def __repr__(self):
    return 'FinalState()'
  
class CharacterState(State):
  def __init__(self, char):
    super(CharacterState, self).__init__()
    self.char = char
  
  def __len__(self):
    return 1
  
  def __str__(self):
    return self.char
  
  def __repr__(self):
    return "CharacterState('%s')" % self.char

class EmptyState(State):
  def __init__(self):
    super(EmptyState, self).__init__()
  
  def __len__(self):
    return 0
  
  def __str__(self):
    return ''
  
  def __repr__(self):
    return 'EmptyState()'
  

class AlternativesState(State):
  def __init__(self, states=None):
    super(AlternativesState, self).__init__()
    if states is None:
      states = []
    self.alternatives = states
  
  def add_alternative(self, alt):
    assert type(alt) == list
    self.alternatives.append(alt)
  
  def __len__(self):
    min_length = 99999
    for alt in self.alternatives:
      min_length = min(min_length, sum(len(a) for a in alt))
    return min_length
  
  def __str__(self):
    acc = '('
    for alt in self.alternatives:
      acc += ''.join(str(step) for step in alt)
      acc += '|'
    acc = acc[:-1] + ')'
    return acc
  
  def __repr__(self):
    acc = 'AlternativesState(['
    for alt in self.alternatives:
      acc += '['
      acc += ', '.join(repr(step) for step in alt)
      acc += '], '
    acc = acc[:-3] + ']])'
    return acc

class Machine(object):
  def __init__(self, stream):
    """
    >>> inp = '^WNE$'
    >>> m = Machine(StringIO(inp))
    >>> str(m)
    '^WNE$'
    >>> repr(m)
    "[InitialState(), CharacterState('W'), CharacterState('N'), CharacterState('E'), FinalState()]"
    
    >>> inp = '^()$'
    >>> m = Machine(StringIO(inp))
    >>> str(m)
    '^()$'
    >>> repr(m)
    '[InitialState(), AlternativesState([[EmptyState()]]), FinalState()]'
    
    >>> inp = '^(WNE)$'
    >>> m = Machine(StringIO(inp))
    >>> str(m) == inp
    True
    >>> repr(m)
    "[InitialState(), AlternativesState([[CharacterState('W'), CharacterState('N'), CharacterState('E')]]), FinalState()]"
    
    >>> inp = '^(WN|E)$'
    >>> m = Machine(StringIO(inp))
    >>> str(m) == inp
    True
    >>> repr(m)
    "[InitialState(), AlternativesState([[CharacterState('W'), CharacterState('N')], [CharacterState('E')]]), FinalState()]"
    
    >>> inp = '^ESSWWN(E|NNENN(EESS(WNSE|)SSS|WWWSSSSE(SW|NNNE)))$'
    >>> m = Machine(StringIO(inp))
    >>> str(m) == inp
    True

    >>> inp = '^WSSEESWWWNW(S|NENNEEEENN(ESSSSW(NWSW|SSEN)|WSWWN(E|WWS(E|SS))))$'
    >>> m = Machine(StringIO(inp))
    >>> str(m) == inp
    True
    
    >>> inp = '^ENWWW(NEEE|SSE(EE|N))$'
    >>> m = Machine(StringIO(inp))
    >>> str(m) == inp
    True
    
    >>> inp = '^ENNWSWW(NEWS|)SSSEEN(WNSE|)EE(SWEN|)NNN$'
    >>> m = Machine(StringIO(inp))
    >>> str(m) == inp
    True
    >>> repr(m)
    "[InitialState(), CharacterState('E'), CharacterState('N'), CharacterState('N'), CharacterState('W'), CharacterState('S'), CharacterState('W'), CharacterState('W'), AlternativesState([[CharacterState('N'), CharacterState('E'), CharacterState('W'), CharacterState('S')], [EmptyState()]]), CharacterState('S'), CharacterState('S'), CharacterState('S'), CharacterState('E'), CharacterState('E'), CharacterState('N'), AlternativesState([[CharacterState('W'), CharacterState('N'), CharacterState('S'), CharacterState('E')], [EmptyState()]]), CharacterState('E'), CharacterState('E'), AlternativesState([[CharacterState('S'), CharacterState('W'), CharacterState('E'), CharacterState('N')], [EmptyState()]]), CharacterState('N'), CharacterState('N'), CharacterState('N'), FinalState()]"
    """
    stack = []

    while True:
      c = stream.read(1)
      # eprint(c)
      if not c:
        break
    
      if c == '^':
        state = InitialState()
        stack.insert(0, (None, [state]))

      elif c == '$':
        state = FinalState()
        stack[0][1].append(state)
        _, machine = stack.pop()
        assert len(stack) == 0
        self.steps = machine
        return

      elif c in 'NEWS':
        state = CharacterState(c)
        stack[0][1].append(state)

      elif c == '(':
        state = AlternativesState()
        stack[0][1].append(state)
        stack.insert(0, (state, []))

      elif c == '|':
        alt, current = stack.pop(0)
        if len(current) > 0:
          alt.add_alternative(current)
        else:
          alt.add_alternative([EmptyState()])
        stack.insert(0, (alt, []))
    
      elif c == ')':
        alt, current = stack.pop(0)
        if len(current) > 0:
          alt.add_alternative(current)
        else:
          alt.add_alternative([EmptyState()])

      else:
        eprint("Got a weird character '%s'" % c)
        assert False
  
    assert False
  
  def bob_iterator(self):
    """
    >>> inp = '^ENWWW(NEEE|SSE(EE|N))$'
    >>> m = Machine(StringIO(inp))
    >>> m.bob_iterator()
    9

    >>> inp = '^ENNWSWW(NEWS|)SSSEEN(WNSE|)EE(SWEN|)NNN$'
    >>> m = Machine(StringIO(inp))
    >>> m.bob_iterator()
    18
    """
    blah = [(self.steps, 0)]
    while len(blah) > 0:
      current, dist = blah.pop(0)
      eprint(current, dist)
      for s in range(len(current) - 1):
        dist += 1
        # current[s].neighbors.append((current[s+1], dist+1)
        blah.append((current[s+1], dist))
        if type(current[s]) == AlternativesState:
          for child in current[s].alternatives:
            # current[s].neighbors.append(child[0], dist)
            blah.append((child, dist))
            
          
    
    # max_terminal = 0
    # blah = [(self.steps[0], 0)]
    # while len(blah) > 0:
    #   current, dist = blah.pop(0)
    #   if len(current.neighbors) == 0:
    #     max_terminal = max(max_terminal, dist)
    #   eprint('curr', current, dist, len(current.neighbors) == 0)
    #   for neigh in current.neighbors:
    #     nextdist = dist + 1
    #     blah.append((neigh, nextdist))
    # return max_terminal
  def __len__(self):
    """
    >>> inp = '^WNE$'
    >>> m = Machine(StringIO(inp))
    >>> len(m)
    3
    
    >>> inp = '^()$'
    >>> m = Machine(StringIO(inp))
    >>> len(m)
    0
    
    >>> inp = '^(WNE)$'
    >>> m = Machine(StringIO(inp))
    >>> len(m)
    3
    
    >>> inp = '^(WN|E)$'
    >>> m = Machine(StringIO(inp))
    >>> # len(m)
    2

    >>> inp = '^ESSWWN(E|NNENN(EESS(WNSE|)SSS|WWWSSSSE(SW|NNNE)))$'
    >>> m = Machine(StringIO(inp))
    >>> len(m)
    23

    >>> inp = '^WSSEESWWWNW(S|NENNEEEENN(ESSSSW(NWSW|SSEN)|WSWWN(E|WWS(E|SS))))$'
    >>> m = Machine(StringIO(inp))
    >>> len(m)
    31
    
    >>> inp = '^ENWWW(NEEE|SSE(EE|N))$'
    >>> m = Machine(StringIO(inp))
    >>> len(m)
    10
    
    >>> inp = '^ENNWSWW(NEWS|)SSSEEN(WNSE|)EE(SWEN|)NNN$'
    >>> m = Machine(StringIO(inp))
    >>> len(m)
    18
    
    """
    # for step in self.steps:
    #   eprint('step', step)
    return sum(len(step) for step in self.steps)
  
  def __str__(self):
    return ''.join(str(step) for step in self.steps)
  
  def __repr__(self):
    return repr(self.steps)


# def woot(machine):
#   """
#   >>> inp = '^ENNWSWW(NEWS|)SSSEEN(WNSE|)EE(SWEN|)NNN$'
#   >>> m = Machine(StringIO(inp))
#   >>> woot(m)
#   """
#   queue = [machine.steps.pop(0)]
#   visited = defaultdict(lambda:False)
#   visited[queue[0]] = True
#
#   while len(queue) > 0:
#     s = queue.pop(0)
#     a_nextnext = machine.steps.pop(0)
#
#     if type(nextnext) == AlternativesState:
#       a_nextnext = a_nextnext.alternatives
#     else:
#       a_nextnext = [a_nextnext]
#
#     eprint('nextnext', repr(nextnext))
#
#
#     if not visited[nextnext]:
#       visited[nextnext] = True
#       queue.append(nextnext)
#     eprint(queue)
#   return 0
  

if len(sys.argv) == 2 and os.path.isfile(sys.argv[1]):
  m = Machine(open(sys.argv[1]))
  
    
  
  
  
  print(len(m))

else:
    import doctest
    doctest.testmod()
