#!/usr/bin/env python3

import sys
from collections import defaultdict

def parse(line):
    part = line[1:].partition(' ')
    num = int(part[0])

    part = part[2][2:].partition(',')
    x = int(part[0])
    
    part = part[2].partition(':')
    y = int(part[0])
    
    part = part[2].partition('x')
    width = int(part[0])

    height = int(part[2])
    
    return (num, x, y, width, height)
    
claims = set()
fabric = defaultdict(lambda: [])
for claim in (parse(line.strip()) for line in sys.stdin.readlines()):
    claims.add(claim[0])
    for x in range(claim[1], claim[1] + claim[3]):
        for y in range(claim[2], claim[2] + claim[4]):
            fabric[(x, y)].append(claim[0])

for (loc, loc_claims) in fabric.items():
    if len(loc_claims)>1:
        for claim in loc_claims:
            claims.discard(claim)

if len(claims)==1:
    print(list(claims)[0])

# candidate_locations=set((a[1][0] for a in filter(lambda x: len(x[1])==1, fabric.items())))
# print(candidate_locations)
# overlaps = len(list(filter(lambda x: len(x)>1, fabric.values())))
# print(overlaps)

# print fabric
# for x in range(1000):
#     for y in range(1000):
#         if fabric[(x, y)] > 1:
#             print('x', end='')
#         elif fabric[(x, y)] > 0:
#             print('o', end='')
#         else:
#             print('.', end='')
#     print('')
