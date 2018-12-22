#!/usr/bin/env python3

"""
>>> inp = r'''
... #######
... #E..G.#
... #...#.#
... #.G.#G#
... #######
... '''
>>> m = Map(StringIO(dedent(inp).strip()))
>>> for unit in list(m.units()):
...     if not m.can_attack(unit):
...         move = m.next_move(unit, m.targets(unit))
...         if move:
...             m.move(unit, move)
>>> m
#######   
#.EG..#   E(200), G(200)
#.G.#.#   G(200)
#...#G#   G(200)
#######   
"""

import sys
from textwrap import dedent
from itertools import product, chain, islice, zip_longest, count
import heapq
from io import StringIO
from collections import defaultdict, namedtuple
import os.path
import math

Loc = namedtuple('Loc', ['x', 'y'])

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    pass

class PriorityQueue(object):
    """
    >>> Q = PriorityQueue()
    >>> Q.add_task('write code', 5)
    >>> Q.add_task('release product', 7)
    >>> Q.add_task('write spec', 1)
    >>> Q.add_task('create tests', 3)
    >>> Q.extract_min()
    'write spec'
    >>> Q.add_task('create tests', 30)
    >>> Q.extract_min()
    'write code'
    """

    REMOVED = '<removed-task>'      # placeholder for a removed task
    
    def __init__(self):
        self.pq = []                         # list of entries arranged in a heap
        self.entry_finder = {}               # mapping of tasks to entries
        self.counter = count()     # unique sequence count
    
    def is_empty(self):
        return len([e for e in self.pq if not e[2] == PriorityQueue.REMOVED]) == 0
    
    def extract_min(self):
        while True:
            entry = heapq.heappop(self.pq)
            if not entry[2] == PriorityQueue.REMOVED:
                return entry[2]
        return False
    
    def add_task(self, task, priority=0):
        'Add a new task or update the priority of an existing task'
        if task in self.entry_finder:
            self.remove_task(task)
        count = next(self.counter)
        entry = [priority, count, task]
        self.entry_finder[task] = entry
        heapq.heappush(self.pq, entry)
    
    def remove_task(self, task):
        'Mark an existing task as REMOVED.  Raise KeyError if not found.'
        entry = self.entry_finder.pop(task)
        entry[-1] = PriorityQueue.REMOVED
    
    def __contains__(self, task):
        return task in self.entry_finder
    
    def __iter__(self):
        for _, _, task in self.pq:
            if not task == PriorityQueue.REMOVED:
                yield task    

class Unit(object):
    hit_points = 200
    attack = 3
    
    def __repr__(self):
        return '%s(%d)' % (self.char(), self.hit_points)

class Goblin(Unit):
    def char(self):
        return 'G'

class Elf(Unit):
    def char(self):
        return 'E'
    
class Map(object):
    """
    >>> inp = r'''
    ... #########
    ... #G..G..G#
    ... #.......#
    ... #.......#
    ... #G..E..G#
    ... #.......#
    ... #.......#
    ... #G..G..G#
    ... #########
    ... '''
    >>> m = Map(StringIO(dedent(inp).strip()))
    >>> m
    #########   
    #G..G..G#   G(200), G(200), G(200)
    #.......#   
    #.......#   
    #G..E..G#   G(200), E(200), G(200)
    #.......#   
    #.......#   
    #G..G..G#   G(200), G(200), G(200)
    #########   
    >>> units = list(m.units())
    >>> units
    [G(200), G(200), G(200), G(200), E(200), G(200), G(200), G(200), G(200)]

    >>> m.targets(units[0])
    {Loc(x=4, y=4): E(200)}
    
    >>> m.targets(units[4])
    {Loc(x=1, y=1): G(200), Loc(x=4, y=1): G(200), Loc(x=7, y=1): G(200), Loc(x=1, y=4): G(200), Loc(x=7, y=4): G(200), Loc(x=1, y=7): G(200), Loc(x=4, y=7): G(200), Loc(x=7, y=7): G(200)}
    
    >>> m.can_attack(units[4])
    []
    
    >>> m.squares_in_range_of_target(units[0])
    {Loc(x=1, y=2), Loc(x=2, y=1)}
    
    >>> [m.squares_in_range_of_target(t) for loc,t in m.targets(units[0]).items()]
    [{Loc(x=4, y=5), Loc(x=5, y=4), Loc(x=3, y=4), Loc(x=4, y=3)}]

    >>> flatten(m.squares_in_range_of_target(t) for loc,t in m.targets(units[4]).items())
    [Loc(x=1, y=2), Loc(x=2, y=1), Loc(x=4, y=2), Loc(x=5, y=1), Loc(x=3, y=1), Loc(x=6, y=1), Loc(x=7, y=2), Loc(x=1, y=5), Loc(x=1, y=3), Loc(x=2, y=4), Loc(x=7, y=3), Loc(x=7, y=5), Loc(x=6, y=4), Loc(x=2, y=7), Loc(x=1, y=6), Loc(x=3, y=7), Loc(x=5, y=7), Loc(x=4, y=6), Loc(x=7, y=6), Loc(x=6, y=7)]

    >>> m = Map(StringIO('G.\\nEE'))
    >>> m
    G.   G(200)
    EE   E(200), E(200)
    >>> units = list(m.units())
    >>> m.can_attack(units[0])
    [(Loc(x=0, y=1), E(200))]
    
    >>> m.can_attack(units[2])
    []
    
    """ 
    
    def __init__(self, inp):
        row_count = 0
        no_wall = []
        yes_wall = []
        goblins = {}
        elves = {}
        for i, l in enumerate(inp.readlines()):
            col_count = 0
            row_count += 1
            for j, c in enumerate(l.strip()):
                col_count += 1
                loc = Loc(j, i)
                if c == '#':
                    yes_wall.append(loc)
                else:
                    no_wall.append(loc)
                if c == 'E':
                    elves[loc] = Elf()
                elif c == 'G':
                    goblins[loc] = Goblin()
        self.yes_wall = yes_wall
        self.no_wall = no_wall
        self.elves = elves
        self.goblins = goblins
        self.size = (col_count, row_count)

    def __repr__(self):
        out = ''
        for i in range(self.size[1]):
            units = []
            for j in range(self.size[0]):
                loc = Loc(j,i)
                if loc in self.yes_wall:
                    out += '#'
                elif loc in self.goblins:
                    out += 'G'
                    units.append(self.goblins[loc])
                elif loc in self.elves:
                    out += 'E'
                    units.append(self.elves[loc])
                else:
                    out += '.'

            out += '   '
            out += ', '.join(str(unit) for unit in units)
            out += '\n'
        return out[:-1]
    
    def units(self):
        """
        >>> inp = r'''
        ... #########
        ... #G..G..G#
        ... #.......#
        ... #.......#
        ... #G..E..G#
        ... #.......#
        ... #.......#
        ... #G..G..G#
        ... #########
        ... '''
        >>> m = Map(StringIO(dedent(inp).strip()))
        >>> units = list(m.units())
        >>> units[0], m._loc_of_unit(units[0])
        (G(200), Loc(x=1, y=1))
        >>> units[1], m._loc_of_unit(units[1])
        (G(200), Loc(x=4, y=1))
        >>> units[2], m._loc_of_unit(units[2])
        (G(200), Loc(x=7, y=1))
        >>> units[3], m._loc_of_unit(units[3])
        (G(200), Loc(x=1, y=4))
        >>> units[4], m._loc_of_unit(units[4])
        (E(200), Loc(x=4, y=4))
        >>> units[5], m._loc_of_unit(units[5])
        (G(200), Loc(x=7, y=4))
        >>> units[6], m._loc_of_unit(units[6])
        (G(200), Loc(x=1, y=7))
        >>> units[7], m._loc_of_unit(units[7])
        (G(200), Loc(x=4, y=7))
        >>> units[8], m._loc_of_unit(units[8])
        (G(200), Loc(x=7, y=7))
        """
        for i in range(self.size[1]):
            for j in range(self.size[0]):
                loc = Loc(j, i)
                if loc in self.goblins:
                    yield self.goblins[loc]
                elif loc in self.elves:
                    yield self.elves[loc]
    
    def targets(self, unit):
        if type(unit) == Goblin:
            return self.elves
        elif type(unit) == Elf:
            return self.goblins
        else:
            assert False

    def are_target_left(self, unit):
        return len(self.targets(unit)) > 0
    
    def squares_in_range_of_target(self, target):
        loc = self._loc_of_unit(target)

        in_range_targets = set()
        for adj in adjacent(loc):
            if adj in self.no_wall and not adj in self.goblins and not adj in self.elves:
                in_range_targets.add(adj)

        return in_range_targets

    def can_attack(self, unit):
        adj = []
        my_loc = self._loc_of_unit(unit)
        for target_loc, target in self.targets(unit).items():
            if target_loc in adjacent(my_loc):
                adj.append((target_loc, target))
        return adj
         
    def move(self, unit, new_loc):
        """
        >>> inp = r'''
        ... #######
        ... #E..G.#
        ... #...#.#
        ... #.G.#G#
        ... #######
        ... '''
        >>> m = Map(StringIO(dedent(inp).strip()))
        >>> units = list(m.units())
        >>> unit = units[0]
        >>> m.move(unit, Loc(1, 2))
        >>> m
        #######   
        #...G.#   G(200)
        #E..#.#   E(200)
        #.G.#G#   G(200), G(200)
        #######   
        >>> m.move(units[1], Loc(5, 1))
        >>> m
        #######   
        #....G#   G(200)
        #E..#.#   E(200)
        #.G.#G#   G(200), G(200)
        #######   

        >>> inp = r'''
        ... #########
        ... #G..G..G#
        ... #.......#
        ... #.......#
        ... #G..E..G#
        ... #.......#
        ... #.......#
        ... #G..G..G#
        ... #########
        ... '''
        >>> m = Map(StringIO(dedent(inp).strip()))
        >>> for unit in list(m.units()):
        ...     move = m.next_move(unit, m.targets(unit))
        ...     if move:
        ...         m.move(unit, move)
        >>> m
        #########   
        #.G...G.#   G(200), G(200)
        #...G...#   G(200)
        #...E..G#   E(200), G(200)
        #.G.....#   G(200)
        #.......#   
        #G..G..G#   G(200), G(200), G(200)
        #.......#   
        #########   
        >>> for unit in list(m.units()):
        ...     move = m.next_move(unit, m.targets(unit))
        ...     if move:
        ...         m.move(unit, move)
        >>> m
        #########   
        #..G.G..#   G(200), G(200)
        #...G...#   G(200)
        #.G.E.G.#   G(200), E(200), G(200)
        #.......#   
        #G..G..G#   G(200), G(200), G(200)
        #.......#   
        #.......#   
        #########   
        >>> for unit in list(m.units()):
        ...     move = m.next_move(unit, m.targets(unit))
        ...     if move:
        ...         m.move(unit, move)
        >>> m
        #########   
        #.......#   
        #..GGG..#   G(200), G(200), G(200)
        #..GEG..#   G(200), E(200), G(200)
        #G..G...#   G(200), G(200)
        #......G#   G(200)
        #.......#   
        #.......#   
        #########   
        """
        assert type(new_loc) == Loc
        loc = self._loc_of_unit(unit)
        assert not new_loc in self.elves
        assert not new_loc in self.goblins
        assert not new_loc in self.yes_wall
        
        if loc in self.elves:
            self.elves.pop(loc)
            self.elves[new_loc] = unit
            
        if loc in self.goblins:
            self.goblins.pop(loc)
            self.goblins[new_loc] = unit

    def attack(self, unit):
        """
        >>> inp = r'''
        ... #######
        ... #EG.G.#
        ... #G..#.#
        ... #.G.#G#
        ... #######
        ... '''
        >>> m = Map(StringIO(dedent(inp).strip()))
        >>> units = list(m.units())
        >>> unit = units[0]
        >>> unit
        E(200)
        >>> m.attack(unit)
        (Loc(x=2, y=1), G(197))
        >>> for i in range(65):
        ...     _ = m.attack(unit)
        >>> m.attack(unit)
        (Loc(x=2, y=1), G(-1))
        >>> m.attack(unit)
        (Loc(x=1, y=2), G(197))

        >>> inp = r'''
        ... G....
        ... ..G..
        ... ..EG.
        ... ..G..
        ... ...G.
        ... '''
        >>> m = Map(StringIO(dedent(inp).strip()))
        >>> points = [9, 4, 100, 2, 2, 1]
        >>> units = list(m.units())
        >>> for i in range(len(points)):
        ...    units[i].hit_points = points[i]
        >>> m
        G....   G(9)
        ..G..   G(4)
        ..EG.   E(100), G(2)
        ..G..   G(2)
        ...G.   G(1)
        >>> _ = m.attack(units[2])
        >>> m
        G....   G(9)
        ..G..   G(4)
        ..E..   E(100)
        ..G..   G(2)
        ...G.   G(1)
        """
        target_loc, target = self.next_attack(unit)
        target.hit_points -= unit.attack
        
        if target.hit_points <= 0:
            if target_loc in self.elves:
                self.elves.pop(target_loc)
            if target_loc in self.goblins:
                self.goblins.pop(target_loc)
        return (target_loc, target)
            
    def play_round(self):
        """
        >>> inp = r'''
        ... ####### 
        ... #.G...# 
        ... #...EG# 
        ... #.#.#G# 
        ... #..G#E# 
        ... #.....# 
        ... ####### 
        ... '''
        >>> m = Map(StringIO(dedent(inp).strip()))
        >>> m
        #######   
        #.G...#   G(200)
        #...EG#   E(200), G(200)
        #.#.#G#   G(200)
        #..G#E#   G(200), E(200)
        #.....#   
        #######   
        >>> m.play_round() 
        True
        >>> m
        #######   
        #..G..#   G(200)
        #...EG#   E(197), G(197)
        #.#G#G#   G(200), G(197)
        #...#E#   E(197)
        #.....#   
        #######   
        >>> m.play_round() 
        True
        >>> m
        #######   
        #...G.#   G(200)
        #..GEG#   G(200), E(188), G(194)
        #.#.#G#   G(194)
        #...#E#   E(194)
        #.....#   
        #######   

        >>> inp = r'''
        ... #######
        ... #.G...#
        ... #...EG#
        ... #.#.#G#
        ... #..G#E#
        ... #.....#
        ... #######
        ... '''
        >>> m = Map(StringIO(dedent(inp).strip()))
        >>> for i in range(26):
        ...    _ = m.play_round()
        >>> m.play_round()
        True
        """
        for unit in list(self.units()):
            if unit.hit_points < 0: continue
            if not self.are_target_left(unit):
                return False
            if not self.can_attack(unit):
                move = self.next_move(unit, self.targets(unit))
                if move:
                    self.move(unit, move)
            if self.can_attack(unit):
                self.attack(unit)
        return True

    def next_attack(self, unit):
        """
        >>> inp = r'''
        ... #######
        ... #EG.G.#
        ... #G..#.#
        ... #.G.#G#
        ... #######
        ... '''
        >>> m = Map(StringIO(dedent(inp).strip()))
        >>> units = list(m.units())
        >>> unit = units[0]
        >>> unit
        E(200)
        >>> m.next_attack(unit)
        (Loc(x=2, y=1), G(200))
        """
        attacks = sorted(((target_loc, target) for target_loc, target in self.can_attack(unit)), key=lambda x: x[1].hit_points)
        if len(attacks) == 0:
            raise Exception("No attacks available")
        return attacks[0]

    def next_move(self, first, targets):
        return self.next_move_blah(first, targets)

    def next_move_blah(self, first, targets):
        """
        >>> inp = r'''
        ... #######
        ... #E..G.#
        ... #...#.#
        ... #.G.#G#
        ... #######
        ... '''
        >>> m = Map(StringIO(dedent(inp).strip()))
        >>> units = list(m.units())
        >>> unit = units[0]
        >>> unit
        E(200)
        >>> targets = m.targets(unit)
        >>> targets
        {Loc(x=4, y=1): G(200), Loc(x=2, y=3): G(200), Loc(x=5, y=3): G(200)}
        >>> m.next_move(unit, targets)
        Loc(x=2, y=1)

        >>> inp = r'''
        ... #######
        ... #.E...#
        ... #.....#
        ... #...G.#
        ... #######
        ... '''
        >>> m = Map(StringIO(dedent(inp).strip()))
        >>> units = list(m.units())
        >>> unit = units[0]
        >>> unit
        E(200)
        >>> targets = m.targets(unit)
        >>> targets
        {Loc(x=4, y=3): G(200)}
        >>> m.next_move(unit, targets)
        Loc(x=3, y=1)

        >>> inp = r'''
        ... #########
        ... #.G...G.#
        ... #...G...#
        ... #...E..G#
        ... #.G.....#
        ... #.......#
        ... #G..G..G#
        ... #.......#
        ... #########
        ... '''
        >>> m = Map(StringIO(dedent(inp).strip()))
        >>> units = list(m.units())
        >>> units[0], m._loc_of_unit(units[0]), m.next_move_naive(units[0], m.targets(units[0]))
        (G(200), Loc(x=2, y=1), Loc(x=3, y=1))
        >>> units[1], m._loc_of_unit(units[1]), m.next_move_naive(units[1], m.targets(units[1]))
        (G(200), Loc(x=6, y=1), Loc(x=5, y=1))
        >>> units[2], m._loc_of_unit(units[2]), m.next_move_naive(units[2], m.targets(units[2]))
        (G(200), Loc(x=4, y=2), False)
        >>> units[3], m._loc_of_unit(units[3]), m.next_move_naive(units[3], m.targets(units[3]))
        (E(200), Loc(x=4, y=3), False)
        >>> units[4], m._loc_of_unit(units[4]), m.next_move_naive(units[4], m.targets(units[4]))
        (G(200), Loc(x=7, y=3), Loc(x=6, y=3))
        >>> units[5], m._loc_of_unit(units[5]), m.next_move_naive(units[5], m.targets(units[5]))
        (G(200), Loc(x=2, y=4), Loc(x=2, y=3))
        >>> units[6], m._loc_of_unit(units[6]), m.next_move_naive(units[6], m.targets(units[6]))
        (G(200), Loc(x=1, y=6), Loc(x=1, y=5))
        >>> units[7], m._loc_of_unit(units[7]), m.next_move_naive(units[7], m.targets(units[7]))
        (G(200), Loc(x=4, y=6), Loc(x=4, y=5))
        >>> units[8], m._loc_of_unit(units[8]), m.next_move_naive(units[8], m.targets(units[8]))
        (G(200), Loc(x=7, y=6), Loc(x=7, y=5))
        """
        if self.can_attack(first):
            return False
        
        first_loc = self._loc_of_unit(first)
        
        paths = {}
        for target_loc, target in targets.items():
            Q = PriorityQueue()
            dist = {}
            prev = defaultdict(lambda: None)
        
            for loc in self.no_wall:
                if loc == target_loc:
                    pass
                elif loc in self.elves or loc in self.goblins:
                    continue
                dist[loc] = math.inf
            dist[first_loc] = 0
            
            for v, v_dist in dist.items():
                Q.add_task(v, v_dist)

            while not Q.is_empty():
                u = Q.extract_min()
                if u == target_loc: continue
                
                for v in (v for v in adjacent(u) if v in Q):
                    if v == target_loc: 
                        pass
                    elif v in self.elves or v in self.goblins:
                        continue

                    alt = dist[u] + 1
                    if alt < dist[v]:
                        dist[v] = alt
                        prev[v] = u
                        Q.add_task(v, alt)

            if not target_loc in prev:
                continue
            u = target_loc
            path = [u]
            while not u == first_loc:
                u = prev[u]
                path.insert(0, u)
            paths[target_loc] = path

        if len(paths) == 0:
            return False
        
        min_length = len(min(paths.items(), key=lambda x: len(x[1]))[1])
        shortest_paths = [path for target, path in paths.items() if len(path) == min_length]
        possible_steps = list(set(p[1] for p in shortest_paths))
        possible_steps.sort(key=lambda tup: (tup[1], tup[0]))
        next_step = possible_steps[0]
        
        return next_step

    def next_move_naive(self, first, targets):
        """
        >>> inp = r'''
        ... #######
        ... #E..G.#
        ... #...#.#
        ... #.G.#G#
        ... #######
        ... '''
        >>> m = Map(StringIO(dedent(inp).strip()))
        >>> units = list(m.units())
        >>> unit = units[0]
        >>> unit
        E(200)
        >>> targets = m.targets(unit)
        >>> targets
        {Loc(x=4, y=1): G(200), Loc(x=2, y=3): G(200), Loc(x=5, y=3): G(200)}
        >>> m.next_move(unit, targets)
        Loc(x=2, y=1)

        >>> inp = r'''
        ... #######
        ... #.E...#
        ... #.....#
        ... #...G.#
        ... #######
        ... '''
        >>> m = Map(StringIO(dedent(inp).strip()))
        >>> units = list(m.units())
        >>> unit = units[0]
        >>> unit
        E(200)
        >>> targets = m.targets(unit)
        >>> targets
        {Loc(x=4, y=3): G(200)}
        >>> m.next_move(unit, targets)
        Loc(x=3, y=1)

        >>> inp = r'''
        ... #########
        ... #.G...G.#
        ... #...G...#
        ... #...E..G#
        ... #.G.....#
        ... #.......#
        ... #G..G..G#
        ... #.......#
        ... #########
        ... '''
        >>> m = Map(StringIO(dedent(inp).strip()))
        >>> units = list(m.units())
        >>> units[0], m._loc_of_unit(units[0]), m.next_move_naive(units[0], m.targets(units[0]))
        (G(200), Loc(x=2, y=1), Loc(x=3, y=1))
        >>> units[1], m._loc_of_unit(units[1]), m.next_move_naive(units[1], m.targets(units[1]))
        (G(200), Loc(x=6, y=1), Loc(x=5, y=1))
        >>> units[2], m._loc_of_unit(units[2]), m.next_move_naive(units[2], m.targets(units[2]))
        (G(200), Loc(x=4, y=2), False)
        >>> units[3], m._loc_of_unit(units[3]), m.next_move_naive(units[3], m.targets(units[3]))
        (E(200), Loc(x=4, y=3), False)
        >>> units[4], m._loc_of_unit(units[4]), m.next_move_naive(units[4], m.targets(units[4]))
        (G(200), Loc(x=7, y=3), Loc(x=6, y=3))
        >>> units[5], m._loc_of_unit(units[5]), m.next_move_naive(units[5], m.targets(units[5]))
        (G(200), Loc(x=2, y=4), Loc(x=2, y=3))
        >>> units[6], m._loc_of_unit(units[6]), m.next_move_naive(units[6], m.targets(units[6]))
        (G(200), Loc(x=1, y=6), Loc(x=1, y=5))
        >>> units[7], m._loc_of_unit(units[7]), m.next_move_naive(units[7], m.targets(units[7]))
        (G(200), Loc(x=4, y=6), Loc(x=4, y=5))
        >>> units[8], m._loc_of_unit(units[8]), m.next_move_naive(units[8], m.targets(units[8]))
        (G(200), Loc(x=7, y=6), Loc(x=7, y=5))
        """
        if self.can_attack(first):
            return False
        
        first_loc = self._loc_of_unit(first)
        connections = {}
        edge = targets.keys()
        found_first = False
        while len(edge) > 0 and not found_first:
            next_edge = []
            for loc in edge:
                for adj in adjacent(loc):
                    if adj == first_loc or (adj in self.no_wall and not adj in self.goblins and not adj in self.elves):
                        if adj not in connections:
                            found_first |= adj == first_loc
                            next_edge.append(adj)
                            connections[adj] = loc
            edge = next_edge

        if first_loc in connections:
            return connections[first_loc]
        else:
            return False

    def next_move_floyd_warshall(self, first, targets):
        """
        >>> inp = r'''
        ... #######
        ... #E..G.#
        ... #...#.#
        ... #.G.#G#
        ... #######
        ... '''
        >>> m = Map(StringIO(dedent(inp).strip()))
        >>> units = list(m.units())
        >>> unit = units[0]
        >>> unit
        E(200)
        >>> targets = m.targets(unit)
        >>> targets
        {Loc(x=4, y=1): G(200), Loc(x=2, y=3): G(200), Loc(x=5, y=3): G(200)}
        >>> m.next_move_floyd_warshall(unit, targets)
        Loc(x=2, y=1)

        >>> inp = r'''
        ... #######
        ... #.E...#
        ... #.....#
        ... #...G.#
        ... #######
        ... '''
        >>> m = Map(StringIO(dedent(inp).strip()))
        >>> units = list(m.units())
        >>> unit = units[0]
        >>> unit
        E(200)
        >>> targets = m.targets(unit)
        >>> targets
        {Loc(x=4, y=3): G(200)}
        >>> m.next_move_floyd_warshall(unit, targets)
        Loc(x=3, y=1)

        >>> inp = r'''
        ... #########
        ... #.G...G.#
        ... #...G...#
        ... #...E..G#
        ... #.G.....#
        ... #.......#
        ... #G..G..G#
        ... #.......#
        ... #########
        ... '''
        >>> m = Map(StringIO(dedent(inp).strip()))
        >>> units = list(m.units())
        >>> units[0], m._loc_of_unit(units[0]), m.next_move_floyd_warshall(units[0], m.targets(units[0]))
        (G(200), Loc(x=2, y=1), Loc(x=3, y=1))
        >>> units[1], m._loc_of_unit(units[1]), m.next_move_floyd_warshall(units[1], m.targets(units[1]))
        (G(200), Loc(x=6, y=1), Loc(x=5, y=1))
        >>> units[2], m._loc_of_unit(units[2]), m.next_move_floyd_warshall(units[2], m.targets(units[2]))
        (G(200), Loc(x=4, y=2), False)
        >>> units[3], m._loc_of_unit(units[3]), m.next_move_floyd_warshall(units[3], m.targets(units[3]))
        (E(200), Loc(x=4, y=3), False)
        >>> units[4], m._loc_of_unit(units[4]), m.next_move_floyd_warshall(units[4], m.targets(units[4]))
        (G(200), Loc(x=7, y=3), Loc(x=6, y=3))
        >>> units[5], m._loc_of_unit(units[5]), m.next_move_floyd_warshall(units[5], m.targets(units[5]))
        (G(200), Loc(x=2, y=4), Loc(x=2, y=3))
        >>> units[6], m._loc_of_unit(units[6]), m.next_move_floyd_warshall(units[6], m.targets(units[6]))
        (G(200), Loc(x=1, y=6), Loc(x=1, y=5))
        >>> units[7], m._loc_of_unit(units[7]), m.next_move_floyd_warshall(units[7], m.targets(units[7]))
        (G(200), Loc(x=4, y=6), Loc(x=4, y=5))
        >>> units[8], m._loc_of_unit(units[8]), m.next_move_floyd_warshall(units[8], m.targets(units[8]))
        (G(200), Loc(x=7, y=6), Loc(x=7, y=5))
        """
        if self.can_attack(first):
            return False
        
        first_loc = self._loc_of_unit(first)
        
        dist = defaultdict(lambda: math.inf)
        nextnext = defaultdict(lambda: None)
        for loc in self.no_wall:
            if loc in self.elves or loc in self.goblins: continue
            for adj in adjacent(loc):
                if adj in self.yes_wall: continue
                dist[(loc, adj)] = 1
                nextnext[(loc, adj)] = adj

        for adj in adjacent(first_loc):
            if adj in self.yes_wall: continue
            dist[(first_loc, adj)] = 1
            nextnext[(first_loc, adj)] = adj
        
        for k_loc in self.no_wall:
            for i_loc in self.no_wall:
                for j_loc in self.no_wall:
                    if dist[(i_loc,j_loc)] > dist[(i_loc,k_loc)] + dist[(k_loc,j_loc)]:
                        dist[(i_loc,j_loc)] = dist[(i_loc,k_loc)] + dist[(k_loc,j_loc)]
                        nextnext[(i_loc,j_loc)] = nextnext[(i_loc,k_loc)]
        paths = {}
        for target_loc, target in targets.items():
            if not nextnext[(first_loc, target_loc)]:
                continue
                
            u = first_loc
            path = [u]
            while not u == target_loc:
                u = nextnext[(u,target_loc)]
                path.append(u)
            paths[target] = path

        if len(paths) == 0:
            return False
        
        min_length = len(min(paths.items(), key=lambda x: len(x[1]))[1])
        shortest_paths = [path for target, path in paths.items() if len(path) == min_length]
        possible_steps = list(set(p[1] for p in shortest_paths))
        possible_steps.sort(key=lambda tup: (tup[1], tup[0]))
        next_step = possible_steps[0]
        
        return next_step

    def play_game(self):
        """
        >>> inp = r'''
        ... ####### 
        ... #.G...# 
        ... #...EG# 
        ... #.#.#G# 
        ... #..G#E# 
        ... #.....# 
        ... ####### 
        ... '''
        >>> m = Map(StringIO(dedent(inp).strip()))
        >>> m.play_game()
        27730

        >>> inp = r'''
        ... #######
        ... #G..#E#
        ... #E#E.E#
        ... #G.##.#
        ... #...#E#
        ... #...E.#
        ... #######
        ... '''
        >>> m = Map(StringIO(dedent(inp).strip()))
        >>> m.play_game()
        36334
     
        >>> inp = r'''
        ... #######
        ... #E..EG#
        ... #.#G.E#
        ... #E.##E#
        ... #G..#.#
        ... #..E#.#
        ... #######
        ... '''
        >>> m = Map(StringIO(dedent(inp).strip()))
        >>> m.play_game()
        39514
        
        >>> inp = r'''
        ... #######
        ... #E.G#.#
        ... #.#G..#
        ... #G.#.G#
        ... #G..#.#
        ... #...E.#
        ... #######
        ... '''
        >>> m = Map(StringIO(dedent(inp).strip()))
        >>> m.play_game()
        27755
        
        >>> inp = r'''
        ... #########
        ... #G......#
        ... #.E.#...#
        ... #..##..G#
        ... #...##..#
        ... #...#...#
        ... #.G...G.#
        ... #.....G.#
        ... #########
        ... '''
        >>> m = Map(StringIO(dedent(inp).strip()))
        >>> m.play_game()
        18740
        
        >>> inp = r'''
        ... ################################
        ... #...############################
        ... ###G.###########################
        ... ##.....#########################
        ... #......#########################
        ... ##G...G.########################
        ... #G.....G########################
        ... ###...G#########################
        ... ###....#########################
        ... ######.G.#######################
        ... #######....#####################
        ... ###..#.....GG...G.E...##########
        ... ##........G...#####...##.#######
        ... #.G..........#######...#..######
        ... #...####G...#########......#####
        ... #..G##.#..G.#########.......####
        ... #...##....E.#########...E.....##
        ... #...##......#########G......####
        ... #...........#########.......####
        ... #............#######...........#
        ... #.....E..G...E#####E...........#
        ... #.G...........G.............E###
        ... #...............E#####.#..######
        ... #..#..G...........####...#######
        ... #..#..............######.#######
        ... ####.#...E.......###############
        ... ########..##...#################
        ... ##...##..###..##################
        ... #.......########################
        ... ##...E..########################
        ... ###......#######################
        ... ################################
        ... '''
        >>> m = Map(StringIO(dedent(inp).strip()))
        >>> m.play_game()
        227290
        """
        eprint("Initial Configuration")
        eprint(self)
        for i in range(1, 100000):
            eprint("Round #%d" % i)
            if not self.play_round():
                eprint(self)    
                break
            eprint(self)    
        eprint("All done!")
        full_rounds = i - 1
        remaining_points = sum(unit.hit_points for unit in self.elves.values()) + sum(unit.hit_points for unit in self.goblins.values())
        outcome = full_rounds * remaining_points
        eprint(full_rounds, remaining_points, outcome)
        return outcome
        

    def _loc_of_unit(self, unit):
        if type(unit) == Goblin:
            return next(loc for loc, u in self.goblins.items() if u == unit)
        elif type(unit) == Elf:
            return next(loc for loc, u in self.elves.items() if u == unit)
        else:
            assert False
    
class Node(object):
    children = []

    def __init__(self, unit, loc):
        self.unit = unit
        self.loc = loc
    
    def add_child(self, unit, loc):
        child = Node(unit, loc)
        self.children.append(child)
        return child

def flatten(listOfLists):
    return list(chain.from_iterable(listOfLists))

def adjacent(loc):
    yield(Loc(loc[0]  , loc[1]-1))
    yield(Loc(loc[0]-1, loc[1]  ))
    yield(Loc(loc[0]+1, loc[1]  ))
    yield(Loc(loc[0]  , loc[1]+1))
    
if len(sys.argv) == 2 and os.path.isfile(sys.argv[1]):
    m = Map(open(sys.argv[1]))
    print(m.play_game())

else:
    import doctest
    doctest.testmod()
