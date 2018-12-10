#!/usr/bin/env python3

import sys
from collections import defaultdict

inp = defaultdict(lambda: [])
lines = (l.strip() for l in sys.stdin.readlines())
for line in lines:
    line = line[10:].partition(',')
    x = int(line[0])
    
    line = line[2].partition('>')
    y = int(line[0])
    
    line = line[2][11:].partition(',')
    vx = int(line[0])
    
    vy = int(line[2][:-1])
    inp[(x,y)].append((vx,vy))

def step(points, time):
    bounds = [0,0,0,0]
    new_points = defaultdict(lambda: [])

    for point_loc in points.keys():
        for point_vel in points[point_loc]:
            new_loc = (point_loc[0]+point_vel[0], point_loc[1]+point_vel[1])
            bounds[0] = min(point_loc[0], bounds[0])
            bounds[1] = min(point_loc[1], bounds[1])
            bounds[2] = max(point_loc[0], bounds[2])
            bounds[3] = max(point_loc[1], bounds[3])
            new_points[new_loc].append(point_vel)

    # print(bounds)
    # print((bounds[2]-bounds[0]) * (bounds[3]-bounds[1]))
    
    
    if abs(time - 10942) < 10:
        for y in range(bounds[1], bounds[3]+1):
            for x in range(bounds[0], bounds[2]+1):
                if (x,y) in points:
                    print('#', end='')
                else:
                    print('.', end='')
            print()
    
    return new_points


for t in range(50000):
    print("\nTime: %d" % t)
    inp = step(inp, t)

# print(inp)
