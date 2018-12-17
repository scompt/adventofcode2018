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

def cart_turns(size, carts):
    """
    >>> size = (10, 10)
    >>> carts = {(2, 0): (1, [0, 0, 4, 4], 3), (9, 3): (2, [2, 2, 9, 5], 3)}
    >>> turns = cart_turns(size, carts)
    >>> next(turns)
    ((2, 0), (1, [0, 0, 4, 4], 3))
    >>> next(turns)
    ((9, 3), (2, [2, 2, 9, 5], 3))
    
    >>> carts = {(9, 3): (2, [2, 2, 9, 5], 3), (2, 0): (1, [0, 0, 4, 4], 3)}
    >>> turns = cart_turns(size, carts)
    >>> next(turns)
    ((2, 0), (1, [0, 0, 4, 4], 3))
    >>> next(turns)
    ((9, 3), (2, [2, 2, 9, 5], 3))
    """
    cart_locs = list(carts.keys())
    cart_locs.sort(key=lambda tup:(tup[1], tup[0]))
    for cart_loc in cart_locs:
        if cart_loc in carts:
            yield((cart_loc, carts[cart_loc]))

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
        for i, c in enumerate(line):
            max_x = max(max_x, i)
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
    ... /---\   
    ... |   |   
    ... | /-+-\ 
    ... | v | | 
    ... \-+-/ | 
    ...   ^   ^ 
    ...   \---/
    ... '''
    >>> state = parse(StringIO(dedent(inp).strip()))
    >>> state = step(*state)
    Traceback (most recent call last):
      File "./second.py", line 343, in step
        raise CrashException(list(new_carts.keys())[0])
    CrashException: (6, 4)

    >>> inp = r'''
    ... /---\   
    ... |   |   
    ... | /-+-\ 
    ... | v | | 
    ... \>+-/ | 
    ...   ^   | 
    ...   \---/
    ... '''
    >>> state = parse(StringIO(dedent(inp).strip()))
    >>> state = step(*state)
    Traceback (most recent call last):
      File "./second.py", line 343, in step
        raise CrashException(list(new_carts.keys())[0])
    CrashException: (2, 4)

    >>> inp = r'''
    ... /---\   
    ... |   |   
    ... | /-+-\ 
    ... | v | | 
    ... \>+</ | 
    ...   ^   | 
    ...   \---/
    ... '''
    >>> state = parse(StringIO(dedent(inp).strip()))
    >>> state = step(*state)
    >>> len(state[1])
    0

    >>> inp = r'''
    ... /<<-\   
    ... |   |   
    ... | /-+-\ 
    ... | | | | 
    ... \-+-/ | 
    ...   |   | 
    ...   \---/
    ... '''
    >>> state = parse(StringIO(dedent(inp).strip()))
    >>> state = step(*state)
    >>> len(state[1])
    2

    >>> inp = r'''
    ... />>-\   
    ... |   |   
    ... | /-+-\ 
    ... | | | | 
    ... \-+-/ | 
    ...   |   | 
    ...   \---/
    ... '''
    >>> state = parse(StringIO(dedent(inp).strip()))
    >>> state = step(*state)
    >>> len(state[1])
    0
    """
    removed = False
    cart_locs = set(carts.keys())
    for cart_loc, cart in cart_turns(size, carts):
        direction, track, next_decision = cart

        if direction == RIGHT:
            new_loc = (cart_loc[0]+1, cart_loc[1])
            if new_loc[0] == track[2] and new_loc[1] == track[3]:
                direction = UP
            elif new_loc[0] == track[2] and new_loc[1] == track[1]:
                direction = DOWN

        elif direction == DOWN:
            new_loc = (cart_loc[0], cart_loc[1]+1)
            if new_loc[1] == track[3] and new_loc[0] == track[0]:
                direction = RIGHT
            elif new_loc[1] == track[3] and new_loc[0] == track[2]:
                direction = LEFT

        elif direction == LEFT:
            new_loc = (cart_loc[0]-1, cart_loc[1])
            if new_loc[0] == track[0] and new_loc[1] == track[1]:
                direction = DOWN
            elif new_loc[0] == track[0] and new_loc[1] == track[3]:
                direction = UP

        elif direction == UP:
            new_loc = (cart_loc[0], cart_loc[1]-1)
            if new_loc[1] == track[1] and new_loc[0] == track[0]:
                direction = RIGHT
            elif new_loc[1] == track[1] and new_loc[0] == track[2]:
                direction = LEFT

        else:
            assert False
        
        if new_loc in intersections:
            if cart[2] != STRAIGHT:
                track = next_track(intersections[new_loc], track)
            direction, next_decision = on_intersection(direction, cart[2])
        
        cart_locs.remove(cart_loc)
        carts.pop(cart_loc)

        if new_loc in cart_locs:
            removed = True
            cart_locs.remove(new_loc)
            carts.pop(new_loc)
            
        else:
            cart_locs.add(new_loc)
            carts[new_loc] = (direction, track, next_decision)

    if removed and len(carts) == 1:
        raise CrashException(list(carts.keys())[0])

    return (tracks, carts, intersections, size)

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
    woot = list(intersection)
    assert len(woot) == 2
    woot.remove(current_track)
    assert len(woot) == 1
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
        print(len(state[1]))
        state = step(*state)

else:
    import doctest
    doctest.testmod()
