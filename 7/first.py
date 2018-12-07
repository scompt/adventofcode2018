#!/usr/bin/env python3

import sys
from collections import defaultdict
from itertools import product

dag = defaultdict(lambda: set())
edges = [(line[5], line[36]) for line in sys.stdin.readlines()]
nodes = set()
prereqs = defaultdict(lambda: set())
for edge_from, edge_to in edges:
    nodes.add(edge_from)
    nodes.add(edge_to)
    dag[edge_from].add(edge_to)
    prereqs[edge_to].add(edge_from)

candidate_nodes = set(node for node in nodes if len(prereqs[node]) == 0)
visited = list()
while len(candidate_nodes) > 0:
    prereq_met_nodes = [node for node in candidate_nodes if all(prereq_node in visited for prereq_node in prereqs[node])]
    prereq_met_nodes.sort()
    next_node = prereq_met_nodes.pop(0)
    candidate_nodes.remove(next_node)
    visited.append(next_node)
    candidate_nodes.update(dag[next_node].difference(set(visited)))
    
print(''.join(visited))