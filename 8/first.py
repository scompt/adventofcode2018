#!/usr/bin/env python3

import sys

offset=0
def parse(inp):
    global offset
    child_count = inp[0+offset]
    metadata_count = inp[1+offset]
    offset += 2
    children = []
    for i in range(child_count):
        child, metadata = parse(inp)
        children.append((child, metadata))
    metadata = inp[offset:offset+metadata_count]
    offset += metadata_count
    return (children, metadata)

inp = [int(i) for i in sys.stdin.read().strip().split(' ')]
tree = parse(inp)

nodes = [tree]
metadata_sum = 0
while len(nodes) != 0:
    node = nodes.pop(0)
    nodes.extend(node[0])
    metadata_sum += sum(node[1])

print(metadata_sum)
