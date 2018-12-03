#!/usr/bin/env python3

import sys
from collections import defaultdict

checksum = [0, 0]
for line in [line.strip() for line in sys.stdin.readlines()]:
    hist = defaultdict(lambda: 0)
    for c in line:
        hist[c] += 1

    counts = hist.values()
    if 2 in counts:
        checksum[0] += 1
    if 3 in counts:
        checksum[1] += 1
    
print(checksum[0] * checksum[1])    
