#!/usr/bin/env python3

import sys
from itertools import product
from collections import defaultdict

SIZE = 300
serial = int(sys.argv[1])

power = {}
for x,y in product(range(1, SIZE+1), range(1, SIZE+1)):
  power[(x,y)] = int(((((x+10)*y)+serial)*(x+10))/100%10)-5

# for y in range(1,SIZE+1):
#   for x in range(1,SIZE+1):
#     print('%4d' % power[(x,y)], end='')
#   print()

blocks = defaultdict(lambda: 0)
for x,y in product(range(1, SIZE+1), range(1, SIZE+1)):
  blocks[(x,y,1)] = power[(x,y)]

for size in range(2,SIZE):
  print(size)
  for y in range(1,2+SIZE-size):
    for x in range(1,2+SIZE-size):
      # print(x,y,size)
      blocks[(x,y,size)] = blocks[(x,y,size-1)]
      dy=size-1
      for dx in range(size):
        blocks[(x,y,size)] += power[(x+dx, y+dy)]
      dx=size-1
      for dy in range(size):
        blocks[(x,y,size)] += power[(x+dx, y+dy)]
      blocks[(x,y,size)] -= power[(x+size-1, y+size-1)]

      # print(x,y,size,blocks[(x,y,size-1)],power[(x+size-1, y+size-1)])

# print()
# for y in range(1,SIZE+1):
#   for x in range(1,SIZE+1):
#     print('%4d' % blocks[(x,y,3)], end='')
#   print()

max_block = max(blocks.items(), key=lambda x: x[1])
print(max_block)
