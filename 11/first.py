#!/usr/bin/env python3

import sys
from itertools import product
from collections import defaultdict

SIZE = 300
BLOCK_SIZE = 3
serial = int(sys.argv[1])

power = {}
for x,y in product(range(1, SIZE+1), range(1, SIZE+1)):
  power[(x,y)] = int(((((x+10)*y)+serial)*(x+10))/100%10)-5

blocks = defaultdict(lambda: 0)
for y in range(1,1+SIZE-BLOCK_SIZE):
    for x in range(1,1+SIZE-BLOCK_SIZE):
      for dx in range(BLOCK_SIZE):
        for dy in range(BLOCK_SIZE):
          blocks[(x,y)] += power[(x+dx, y+dy)]

max_block = max(blocks.items(), key=lambda x: x[1])
print(max_block)
