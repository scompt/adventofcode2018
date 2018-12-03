#!/usr/bin/env python3

import sys
from itertools import combinations, zip_longest
from collections import defaultdict

def distance(one, two):
    return sum(a[0]==a[1] for a in zip_longest(one, two))

def output(one, two):
    return ''.join(a[0] for a in zip_longest(one, two) if a[0]==a[1])

checksum = [0, 0]
lines = [line.strip() for line in sys.stdin.readlines()]
combs = combinations(lines, 2)
distances = ((a, distance(*a)) for a in combs)
most_similar = max(distances, key=lambda x: x[1])

print(output(*most_similar[0]))
