#!/usr/bin/env python3

import sys
from itertools import cycle

total = 0
seen = set()
seen.add(total)

inp = cycle([int(line.strip()) for line in sys.stdin.readlines()])
for num in inp:
    total += num
    
    if total in seen:
        print(total)
        sys.exit()
    else:
        seen.add(total)