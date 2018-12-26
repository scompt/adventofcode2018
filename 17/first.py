#!/usr/bin/env python3

"""
>>> inp = r'''
... x=495, y=2..7
... y=7, x=495..501
... x=501, y=3..7
... x=498, y=2..4
... x=506, y=1..2
... x=498, y=10..13
... x=504, y=10..13
... y=13, x=498..504
... '''
>>> clay, size = parse(StringIO(dedent(inp).strip()))
>>> settled_water = set()
>>> flowing_water = [SPRING_LOC]
>>> for i in range(100):
...   settled_water, flowing_water = step(clay, size, settled_water, flowing_water)
...   print_state(clay, size, settled_water, flowing_water)
>>> print_state(clay, size, settled_water, flowing_water)
·····+······
·····|·····#
#··#||·····#
#··#~~#·····
#··#~~#·····
#~~~~~#·····
#~~~~~#·····
#######·····
············
············
···#·····#··
···#·····#··
···#·····#··
···#######··

>>> settled_water, flowing_water = step(clay, size, settled_water, flowing_water)
>>> print_state(clay, size, settled_water, flowing_water)
·····+······
·····|·····#
#··#||·····#
#··#~~#·····
#··#~~#·····
#~~~~~#·····
#~~~~~#·····
#######·····
············
············
···#·····#··
···#·····#··
···#·····#··
···#######··
"""

import sys
from textwrap import dedent
from itertools import product, chain
from io import StringIO
import os.path

SPRING_LOC = (500, 0)


def parse(stream):
    """
    >>> inp = r'''
    ... x=495, y=2..7
    ... y=7, x=495..501
    ... x=501, y=3..7
    ... x=498, y=2..4
    ... x=506, y=1..2
    ... x=498, y=10..13
    ... x=504, y=10..13
    ... y=13, x=498..504
    ... '''
    >>> clay, size = parse(StringIO(dedent(inp).strip()))
    >>> sorted(list(clay), key=lambda tup:(tup[0], tup[1]))
    [(495, 2), (495, 3), (495, 4), (495, 5), (495, 6), (495, 7), (496, 7), (497, 7), (498, 2), (498, 3), (498, 4), (498, 7), (498, 10), (498, 11), (498, 12), (498, 13), (499, 7), (499, 13), (500, 7), (500, 13), (501, 3), (501, 4), (501, 5), (501, 6), (501, 7), (501, 13), (502, 13), (503, 13), (504, 10), (504, 11), (504, 12), (504, 13), (506, 1), (506, 2)]
    >>> size
    (495, 0, 506, 13)
    """
    clay = set()
    for line in stream.readlines():
        x_str, y_str = (l[2:] for l in sorted(line.strip().split(', ')))

        if '..' in x_str:
            a=[int(l) for l in x_str.split('..')]
            xs = range(a[0], a[1] + 1)
        else:
            xs = [int(x_str)]

        if '..' in y_str:
            a=[int(l) for l in y_str.split('..')]
            ys = range(a[0], a[1] + 1)
        else:
            ys = [int(y_str)]
        
        clay.update(set(product(xs, ys)))

    size = [SPRING_LOC[0], SPRING_LOC[1], SPRING_LOC[0], SPRING_LOC[1]]
    for loc in clay:
        size[0] = min(size[0], loc[0])
        size[2] = max(size[2], loc[0])
        size[1] = min(size[1], loc[1])
        size[3] = max(size[3], loc[1])
        
    return (clay, tuple(size))

def print_state(clay, size, settled_water, flowing_water):
    """
    >>> clay = set((500, 1))
    >>> size = (499, 0, 501, 1)
    >>> settled_water = set()
    >>> flowing_water = []
    >>> print_state(clay, size, settled_water, flowing_water)
    ·+·
    ···
    
    >>> clay = set([(495, 2), (495, 3), (495, 4), (495, 5), (495, 6), (495, 7), (496, 7), (497, 7), (498, 2), (498, 3), (498, 4), (498, 7), (498, 10), (498, 11), (498, 12), (498, 13), (499, 7), (499, 13), (500, 7), (500, 13), (501, 3), (501, 4), (501, 5), (501, 6), (501, 7), (501, 13), (502, 13), (503, 13), (504, 10), (504, 11), (504, 12), (504, 13), (506, 1), (506, 2)])
    >>> size = (495, 0, 506, 13)
    >>> print_state(clay, size, settled_water, flowing_water)
    ·····+······
    ···········#
    #··#·······#
    #··#··#·····
    #··#··#·····
    #·····#·····
    #·····#·····
    #######·····
    ············
    ············
    ···#·····#··
    ···#·····#··
    ···#·····#··
    ···#######··
    >>> flowing_water = [(500, 1), (500, 0)]
    >>> print_state(clay, size, settled_water, flowing_water)
    ·····+······
    ·····|·····#
    #··#·······#
    #··#··#·····
    #··#··#·····
    #·····#·····
    #·····#·····
    #######·····
    ············
    ············
    ···#·····#··
    ···#·····#··
    ···#·····#··
    ···#######··
    """
    for y in range(size[1], size[3]+1):
        for x in range(size[0], size[2]+1):
            loc = (x, y)
            if loc in clay:
                print('#', end='')
            elif loc in settled_water:
                print('~', end='')
            elif loc == SPRING_LOC:
                print('+', end='')
            elif loc in flowing_water:
                print('|', end='')
            else:
                print('·', end='')
        print()

def step(clay, size, settled_water, flowing_water):
    """
    >>> settled_water = set()
    >>> clay = set([(495, 2)])
    >>> size = (498, 0, 502, 3)
    >>> flowing_water = [SPRING_LOC]
    >>> _, flowing_water = step(clay, size, settled_water, flowing_water)
    >>> flowing_water
    [(500, 1), (500, 0)]
    >>> settled_water, flowing_water = step(clay, size, settled_water, flowing_water)
    >>> flowing_water
    [(500, 2), (500, 1), (500, 0)]
    
    >>> clay = set([(500, 1)])
    >>> flowing_water = [SPRING_LOC]
    >>> settled_water, flowing_water = step(clay, size, settled_water, flowing_water)
    >>> flowing_water
    [(499, 0), (500, 0)]
    
    >>> clay = set([(500, 1), (499, 0)])
    >>> flowing_water = [SPRING_LOC]
    >>> settled_water, flowing_water = step(clay, size, settled_water, flowing_water)
    >>> flowing_water
    [(501, 0), (500, 0)]
    
    >>> flowing_water = [SPRING_LOC]
    >>> for i in range(3):
    ...   settled_water, flowing_water = step(clay, size, settled_water, flowing_water)
    >>> print_state(clay, size, settled_water, flowing_water)
    ·#+|·
    ··#|·
    ···|·
    ·····
    
    >>> flowing_water = [SPRING_LOC]
    >>> clay = set([(500, 2), (499, 1), (501, 1), (499, 0), (501, 0)])
    >>> for i in range(2):
    ...   settled_water, flowing_water = step(clay, size, settled_water, flowing_water)
    >>> print_state(clay, size, settled_water, flowing_water)
    ·#+#·
    ·#~#·
    ··#··
    ·····

    >>> flowing_water = [SPRING_LOC]
    >>> settled_water = set()
    >>> clay = set([(500, 2), (499, 2), (498, 1), (501, 1), (498, 0), (501, 0)])
    >>> for i in range(6):
    ...   settled_water, flowing_water = step(clay, size, settled_water, flowing_water)
    >>> print_state(clay, size, settled_water, flowing_water)
    #~+#·
    #~~#·
    ·##··
    ·····
    """
    next_flow = flowing_water[0]
    flowing_x, flowing_y = next_flow
    down, left, right = list(next_positions(size, next_flow))
    
    if down not in clay:
        flowing_water.insert(0, down)
    else:
        if left not in chain(clay, flowing_water, settled_water):
            flowing_water.insert(0, left)

        if right not in chain(clay, flowing_water, settled_water):
            flowing_water.insert(0, right)
        
        if next_flow == flowing_water[0]:
            settled_water.add(next_flow)
            flowing_water.pop(0)
    
    return (settled_water, flowing_water)

def next_positions(size, origin):    
    flowing_x, flowing_y = origin
    for x,y in [(flowing_x, flowing_y+1), (flowing_x-1, flowing_y), (flowing_x+1, flowing_y)]:
        if x > size[0] and x <= size[2] and y > size[1] and y <= size[3]:
            yield((x,y))
        else:
            yield(None)

if len(sys.argv) == 2 and os.path.isfile(sys.argv[1]):
    clay, size = parse(open(sys.argv[1]))
    print_state(clay, size, set(), [SPRING_LOC])

else:
    import doctest
    doctest.testmod()
