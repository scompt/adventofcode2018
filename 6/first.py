#!/usr/bin/env python3

import sys
from collections import defaultdict
from itertools import product

coords = [tuple(int(l) for l in line.strip().split(', ')) for line in sys.stdin.readlines()]

xs = [coord[0] for coord in coords]
ys = [coord[1] for coord in coords]

x_min = min(xs)
x_max = max(xs)
y_min = min(ys)
y_max = max(ys)

by_x=defaultdict(lambda: set())
by_y=defaultdict(lambda: set())

for coord in coords:
    by_x[coord[0]].add(coord)
    by_y[coord[1]].add(coord)

finite = []

for x,y in coords:
    if x>x_min and x<x_max and y>y_min and y<y_max:
        finite.append((x,y))
    elif (x==x_min or x==x_max) and (len([other[1]>=y for other in by_x[x]]) == 0 or len([other[1]<=y for other in by_x[x]]) == 0):
        finite.append((x,y))
    elif (y==y_min or y==y_max) and (len([other[0]>=x for other in by_y[y]]) == 0 or len([other[0]<=x for other in by_y[y]]) == 0):
        finite.append((x,y))

class Continue(Exception): pass

expand=0
while True:
    try:
        candidates = product(range(x_min-expand, x_max+expand), range(y_min-expand, y_max+expand))
        distances=defaultdict(lambda: 0)

        for x, y in candidates:
            candidate_distances = {c: abs(c[0]-x) + abs(c[1]-y) for c in coords}
            closest = min(candidate_distances.items(), key=lambda x: candidate_distances[x[0]])
            if closest in finite:
                expand += 1
                raise Continue()

            is_multiple = list(candidate_distances.values()).count(closest[1]) > 1
            if not is_multiple:
                distances[closest[0]] += 1
        break

    except ContinueI:
        continue

max_point = max({f: distances[f] for f in finite}.items(), key=lambda x: distances[x[0]])
print(max_point)