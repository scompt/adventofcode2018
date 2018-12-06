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

under_threshold=set()
distance_cache={}
threshold=10000
expand = 0
last_count=0

while True:
    candidates = product(range(x_min-expand, x_max+expand), range(y_min-expand, y_max+expand))
    
    for x, y in candidates:
        if (x,y) in distance_cache:
            total_distance = distance_cache[(x,y)]
        else:
            total_distance = sum(abs(c[0]-x) + abs(c[1]-y) for c in coords)
            distance_cache[(x,y)] = total_distance
        
        if total_distance < threshold:
            under_threshold.add((x,y))
    
    if len(under_threshold) > last_count:
        expand += 1
        last_count = len(under_threshold)
    else:
        break

print(len(under_threshold))