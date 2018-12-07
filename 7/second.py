#!/usr/bin/env python3

import sys
from collections import defaultdict
from itertools import product

NUM_WORKERS=5
NODE_TIME_OFFSET=-4

workers = [None] * NUM_WORKERS
dag = defaultdict(lambda: set())
edges = [(line[5], line[36]) for line in sys.stdin.readlines()]
nodes = set()
prereqs = defaultdict(lambda: set())
for edge_from, edge_to in edges:
    nodes.add(edge_from)
    nodes.add(edge_to)
    dag[edge_from].add(edge_to)
    prereqs[edge_to].add(edge_from)

current_time = 0
candidate_nodes = set(node for node in nodes if len(prereqs[node]) == 0)
finish_times = defaultdict(lambda: 0)
visited = list()
finished = set()
while not (len(visited) == len(nodes) and all(w is None for w in workers)):
    for i,w in enumerate(workers):
        if w and finish_times[w]==current_time:
            candidate_nodes.update(dag[w].difference(set(visited)))
            visited.append(w)
            workers[i]=None
    
    while len(candidate_nodes) > 0 and None in workers:
        prereq_met_nodes = [node for node in candidate_nodes if all(prereq_node in visited for prereq_node in prereqs[node])]
        if len(prereq_met_nodes) == 0: break
        prereq_met_nodes.sort()
        next_node = prereq_met_nodes.pop(0)
        candidate_nodes.remove(next_node)
        finish_times[next_node] = current_time+ord(next_node)+NODE_TIME_OFFSET
        workers[workers.index(None)] = next_node
    
    current_time += 1
    
print(finish_times[visited[-1]])
