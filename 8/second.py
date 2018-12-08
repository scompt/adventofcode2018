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

def sum_children(node):
    if len(node[0]) == 0:
        nodes = [(node)]
        metadata_sum = 0
        while len(nodes) != 0:
            node = nodes.pop(0)
            nodes.extend(node[0])
            metadata_sum += sum(node[1])
        return metadata_sum
    
    val = 0
    for index in node[1]:
        child_count = len(node[0])
        if index > 0 and index <= child_count:
            val += sum_children(node[0][index-1])
    return val

inp = [int(i) for i in sys.stdin.read().strip().split(' ')]
tree = parse(inp)
output = sum_children(tree)

print(output)
