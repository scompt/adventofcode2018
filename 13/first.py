#!/usr/bin/env python3

import sys
from textwrap import dedent
from io import StringIO
import os.path

CART_DIRECTIONS = ['^', '>', 'v', '<']
UP = CART_DIRECTIONS.index('^')
RIGHT = CART_DIRECTIONS.index('>')
DOWN = CART_DIRECTIONS.index('v')
LEFT = CART_DIRECTIONS.index('<')
STRAIGHT = len(CART_DIRECTIONS)

class CrashException(Exception):
    def __init__(self, loc):
        self.loc = loc

def eprint(*args, **kwargs):
    # print(*args, file=sys.stderr, **kwargs)
    pass

def parse(stream):
    """
    >>> inp = r'''
    ... /----\ 
    ... |    | 
    ... |    | 
    ... \----/ 
    ... '''
    >>> parse(StringIO(dedent(inp).strip()))
    ([[0, 0, 5, 3]], {}, {}, (6, 4))

    >>> inp = r'''
    ... /-----\    
    ... |     |    
    ... |  /--+--\ 
    ... |  |  |  | 
    ... \--+--/  | 
    ...    |     | 
    ...    \-----/ 
    ... '''
    >>> parse(StringIO(dedent(inp).strip()))
    ([[0, 0, 6, 4], [3, 2, 9, 6]], {}, {(6, 2): ([0, 0, 6, 4], [3, 2, 9, 6]), (3, 4): ([3, 2, 9, 6], [0, 0, 6, 4])}, (10, 7))
    
    >>> inp = r'''
    ... /->-\         
    ... |   |  /----\ 
    ... | /-+--+-\  | 
    ... | | |  | v  | 
    ... \-+-/  \-+--/ 
    ...   \------/    
    ... '''
    >>> tracks, carts, intersections, size = parse(StringIO(dedent(inp).strip()))
    >>> tracks
    [[0, 0, 4, 4], [7, 1, 12, 4], [2, 2, 9, 5]]
    >>> carts
    {(2, 0): (1, [0, 0, 4, 4], 3), (9, 3): (2, [2, 2, 9, 5], 3)}
    >>> intersections
    {(4, 2): ([0, 0, 4, 4], [2, 2, 9, 5]), (7, 2): ([7, 1, 12, 4], [2, 2, 9, 5]), (2, 4): ([2, 2, 9, 5], [0, 0, 4, 4]), (9, 4): ([2, 2, 9, 5], [7, 1, 12, 4])}
    >>> size
    (13, 6)
    """
    max_x = float('-inf')

    incomplete_tracks_by_row = {}
    incomplete_tracks_by_col = {}
    tracks = []
    carts = {}
    intersections = {}
    for line_num, line in enumerate(k.rstrip() for k in stream.readlines()):
        # eprint(incomplete_y_tracks)
        eprint(line_num, line)
        for i, c in enumerate(line):
            max_x = max(max_x, i)
            eprint('zz', c, i, incomplete_tracks_by_col.get(i))
            if c == '/':
                if line_num in incomplete_tracks_by_row:
                    track = incomplete_tracks_by_col[i]
                    track[3] = line_num
                    incomplete_tracks_by_col.pop(track[0], None)
                    incomplete_tracks_by_row.pop(track[1], None)
                    incomplete_tracks_by_col.pop(track[2], None)
                    incomplete_tracks_by_row.pop(track[3], None)
                    tracks.append(track)
                    
                else:
                    track = [i, line_num, None, None]
                    incomplete_tracks_by_row[line_num] = track
                    incomplete_tracks_by_col[i] = track

            elif c == '\\':
                if line_num in incomplete_tracks_by_row:
                    track = incomplete_tracks_by_row[line_num]
                    del incomplete_tracks_by_row[line_num]
                    track[2] = i
                    incomplete_tracks_by_col[i] = track
                elif i in incomplete_tracks_by_col:
                    track = incomplete_tracks_by_col[i]
                    del incomplete_tracks_by_col[i]
                    incomplete_tracks_by_row[line_num] = track
                else:
                    eprint(c, i, line_num)
                    assert False
            elif c == '+':
                intersections[(i,line_num)] = (incomplete_tracks_by_col[i], incomplete_tracks_by_row[line_num])
            
            elif c in CART_DIRECTIONS:
                direction = CART_DIRECTIONS.index(c)
                if i in incomplete_tracks_by_col:
                    track = incomplete_tracks_by_col[i]
                elif line_num in incomplete_tracks_by_row:
                    track = incomplete_tracks_by_row[line_num]
                else:
                    assert False
                carts[(i, line_num)] = (direction, track, LEFT)
                    
    assert len(incomplete_tracks_by_col) == 0
    assert len(incomplete_tracks_by_row) == 0
    return (tracks, carts, intersections, (max_x + 1, line_num + 1))

def step(tracks, carts, intersections, size):
    """
    >>> inp = r'''
    ... /----\ 
    ... |    | 
    ... |    | 
    ... \----/ 
    ... '''
    >>> initial = parse(StringIO(dedent(inp).strip()))
    >>> step(*initial)
    ([[0, 0, 5, 3]], {}, {}, (6, 4))
    
    >>> inp = r'''
    ... /->-\         
    ... |   |  /----\ 
    ... | /-+--+-\  | 
    ... | | |  | v  | 
    ... \-+-/  \-+--/ 
    ...   \------/    
    ... '''
    >>> initial = parse(StringIO(dedent(inp).strip()))
    >>> tracks, carts, intersections, _ = step(*initial)
    >>> tracks
    [[0, 0, 4, 4], [7, 1, 12, 4], [2, 2, 9, 5]]
    >>> carts
    {(3, 0): (1, [0, 0, 4, 4], 3), (9, 4): (1, [7, 1, 12, 4], 4)}
    >>> intersections
    {(4, 2): ([0, 0, 4, 4], [2, 2, 9, 5]), (7, 2): ([7, 1, 12, 4], [2, 2, 9, 5]), (2, 4): ([2, 2, 9, 5], [0, 0, 4, 4]), (9, 4): ([2, 2, 9, 5], [7, 1, 12, 4])}

    >>> inp = r'''
    ... /->-\         
    ... |   |  /---<\ 
    ... | /-+--+-\  | 
    ... | | |  | |  | 
    ... \-+-/  \-+--/ 
    ...   \------/    
    ... '''
    >>> initial = parse(StringIO(dedent(inp).strip()))
    >>> tracks, carts, intersections, _ = step(*initial)
    >>> tracks
    [[0, 0, 4, 4], [7, 1, 12, 4], [2, 2, 9, 5]]
    >>> carts
    {(3, 0): (1, [0, 0, 4, 4], 3), (10, 1): (3, [7, 1, 12, 4], 3)}
    >>> intersections
    {(4, 2): ([0, 0, 4, 4], [2, 2, 9, 5]), (7, 2): ([7, 1, 12, 4], [2, 2, 9, 5]), (2, 4): ([2, 2, 9, 5], [0, 0, 4, 4]), (9, 4): ([2, 2, 9, 5], [7, 1, 12, 4])}

    >>> inp = r'''
    ... /---\         
    ... |   |  /----\ 
    ... ^ /-+--+-\  | 
    ... | | |  | |  | 
    ... \-+-/  \-+--/ 
    ...   \------/    
    ... '''
    >>> initial = parse(StringIO(dedent(inp).strip()))
    >>> tracks, carts, intersections, _ = step(*initial)
    >>> tracks
    [[0, 0, 4, 4], [7, 1, 12, 4], [2, 2, 9, 5]]
    >>> carts
    {(0, 1): (0, [0, 0, 4, 4], 3)}
    >>> intersections
    {(4, 2): ([0, 0, 4, 4], [2, 2, 9, 5]), (7, 2): ([7, 1, 12, 4], [2, 2, 9, 5]), (2, 4): ([2, 2, 9, 5], [0, 0, 4, 4]), (9, 4): ([2, 2, 9, 5], [7, 1, 12, 4])}

    >>> inp = r'''
    ... /---\         
    ... ^   |  /----\ 
    ... | /-+--+-\  | 
    ... | | |  | |  | 
    ... \-+-/  \-+--/ 
    ...   \------/    
    ... '''
    >>> initial = parse(StringIO(dedent(inp).strip()))
    >>> tracks, carts, intersections, _ = step(*initial)
    >>> tracks
    [[0, 0, 4, 4], [7, 1, 12, 4], [2, 2, 9, 5]]
    >>> carts
    {(0, 0): (1, [0, 0, 4, 4], 3)}
    >>> intersections
    {(4, 2): ([0, 0, 4, 4], [2, 2, 9, 5]), (7, 2): ([7, 1, 12, 4], [2, 2, 9, 5]), (2, 4): ([2, 2, 9, 5], [0, 0, 4, 4]), (9, 4): ([2, 2, 9, 5], [7, 1, 12, 4])}

    >>> inp = r'''
    ... /-->\         
    ... ^   | 
    ... |   | 
    ... |   v 
    ... \<--/ 
    ... '''
    >>> initial = parse(StringIO(dedent(inp).strip()))
    >>> tracks, carts, intersections, _ = step(*initial)
    >>> tracks
    [[0, 0, 4, 4]]
    >>> carts
    {(4, 0): (2, [0, 0, 4, 4], 3), (0, 0): (1, [0, 0, 4, 4], 3), (4, 4): (3, [0, 0, 4, 4], 3), (0, 4): (0, [0, 0, 4, 4], 3)}
    >>> intersections
    {}
    
    >>> inp = r'''
    ... /<--\         
    ... |   ^ 
    ... |   | 
    ... v   | 
    ... \-->/ 
    ... '''
    >>> initial = parse(StringIO(dedent(inp).strip()))
    >>> tracks, carts, intersections, _ = step(*initial)
    >>> tracks
    [[0, 0, 4, 4]]
    >>> carts
    {(0, 0): (2, [0, 0, 4, 4], 3), (4, 0): (3, [0, 0, 4, 4], 3), (0, 4): (1, [0, 0, 4, 4], 3), (4, 4): (0, [0, 0, 4, 4], 3)}
    >>> intersections
    {}
    
    >>> inp = r'''
    ... /-----\    
    ... |     v    
    ... |  /--+--\ 
    ... |  |  |  | 
    ... \--+--/  | 
    ...    |     | 
    ...    \-----/ 
    ... '''
    >>> initial = parse(StringIO(dedent(inp).strip()))
    >>> tracks, carts, intersections, _ = step(*initial)
    >>> carts
    {(6, 2): (1, [3, 2, 9, 6], 4)}

    >>> inp = r'''
    ... /-----\    
    ... |     v    
    ... |  /--+<-\ 
    ... |  |  |  | 
    ... \--+--/  | 
    ...    |     | 
    ...    \-----/ 
    ... '''
    >>> initial = parse(StringIO(dedent(inp).strip()))
    >>> tracks, carts, intersections = step(*initial)
    Traceback (most recent call last):
      File "./first.py", line 290, in step
        raise CrashException(new_loc)
    CrashException: (6, 2)
    
    >>> inp = r'''
    ... /->-\         
    ... |   |  /----\ 
    ... | /-+--+-\  | 
    ... | | |  | v  | 
    ... \-+-/  \-+--/ 
    ...   \------/    
    ... '''
    >>> state = parse(StringIO(dedent(inp).strip()))
    >>> for i in range(20):
    ...   state = step(*state)
    ...   state[1]
    Traceback (most recent call last):
      File "./first.py", line 354, in step
        raise CrashException(new_loc)
    CrashException: (7, 3)
    """
    new_cart_locs = set()
    new_carts = {}
    for cart_loc, cart in carts.items():
        new_track = cart[1]
        if cart[0] == RIGHT:
            new_loc = (cart_loc[0]+1, cart_loc[1])
            eprint(new_loc, cart_loc, cart[1])
            next_decision = cart[2]
            if new_loc[0] == cart[1][2]:
                if new_loc[1] == cart[1][3]:
                    new_direction = UP
                else:
                    new_direction = DOWN
            elif new_loc in intersections:
                if cart[2] != STRAIGHT:
                    new_track = next_track(intersections[new_loc], cart[1])
                new_direction, next_decision = on_intersection(cart[0], cart[2])
                eprint(new_loc, new_direction, new_track)
            else:
                new_direction = cart[0]
            new_carts[new_loc] = (new_direction, new_track, next_decision)

        elif cart[0] == DOWN:
            new_loc = (cart_loc[0], cart_loc[1]+1)
            next_decision = cart[2]
            if new_loc[1] == cart[1][3]:
                if new_loc[0] == cart[1][0]:
                    new_direction = RIGHT
                else:
                    new_direction = LEFT
            elif new_loc in intersections:
                if cart[2] != STRAIGHT:
                    new_track = next_track(intersections[new_loc], cart[1])
                new_direction, next_decision = on_intersection(cart[0], cart[2])
                eprint(new_loc, new_direction, new_track)
            else:
                new_direction = cart[0]
            new_carts[new_loc] = (new_direction, new_track, next_decision)

        elif cart[0] == LEFT:
            new_loc = (cart_loc[0]-1, cart_loc[1])
            next_decision = cart[2]
            if new_loc[0] == cart[1][0]:
                if new_loc[1] == cart[1][1]:
                    new_direction = DOWN
                else:
                    new_direction = UP
            elif new_loc in intersections:
                if cart[2] != STRAIGHT:
                    new_track = next_track(intersections[new_loc], cart[1])
                new_direction, next_decision = on_intersection(cart[0], cart[2])
                eprint(new_loc, new_direction, new_track)
            else:
                new_direction = cart[0]
            new_carts[new_loc] = (new_direction, new_track, next_decision)

        elif cart[0] == UP:
            new_loc = (cart_loc[0], cart_loc[1]-1)
            next_decision = cart[2]
            if new_loc[1] == cart[1][1]:
                if new_loc[0] == cart[1][2]:
                    new_direction = LEFT
                else:
                    new_direction = RIGHT
            elif new_loc in intersections:
                if cart[2] != STRAIGHT:
                    new_track = next_track(intersections[new_loc], cart[1])
                new_direction, next_decision = on_intersection(cart[0], cart[2])
                eprint(new_loc, new_direction, new_track)
            else:
                new_direction = cart[0]
            new_carts[new_loc] = (new_direction, new_track, next_decision)

        else:
            assert False
        
        if new_loc in new_cart_locs:
            raise CrashException(new_loc)
        else:
            new_cart_locs.add(new_loc)

    return (tracks, new_carts, intersections, size)

DECISIONS = {(UP, LEFT):        (LEFT, STRAIGHT),
             (UP, STRAIGHT):    (UP, RIGHT),
             (UP, RIGHT):       (RIGHT, LEFT),
             (RIGHT, LEFT):     (UP, STRAIGHT),
             (RIGHT, STRAIGHT): (RIGHT, RIGHT),
             (RIGHT, RIGHT):    (DOWN, LEFT),
             (DOWN, LEFT):      (RIGHT, STRAIGHT),
             (DOWN, STRAIGHT):  (DOWN, RIGHT),
             (DOWN, RIGHT):     (LEFT, LEFT),
             (LEFT, LEFT):      (DOWN, STRAIGHT),
             (LEFT, STRAIGHT):  (LEFT, RIGHT),
             (LEFT, RIGHT):     (UP, LEFT)}

def next_track(intersection, current_track):
    """
    >>> current_track = [3, 2, 9, 6]
    >>> intersection = ([3, 2, 9, 6], [0, 0, 6, 4])
    >>> current_track = next_track(intersection, current_track)
    >>> current_track
    [0, 0, 6, 4]
    >>> current_track = next_track(intersection, current_track)
    >>> current_track
    [3, 2, 9, 6]
    """
    eprint('qq', intersection, current_track)
    woot = list(intersection)
    woot.remove(current_track)
    return woot[0]
    

def on_intersection(current_direction, next_decision):
    """
    >>> on_intersection(UP, LEFT)
    (3, 4)
    >>> on_intersection(UP, STRAIGHT)
    (0, 1)
    >>> on_intersection(UP, RIGHT)
    (1, 3)
    """
    return DECISIONS[(current_direction, next_decision)]

if len(sys.argv) == 2 and os.path.isfile(sys.argv[1]):
    state = parse(open(sys.argv[1]))
    while(True):
        state = step(*state)

else:
    import doctest
    doctest.testmod()
