#!/usr/bin/env python3

import sys
from collections import defaultdict

def print_state(player_number, circle, current_marble, scores):
    print('[%d] ' % (player_number+1), end='')
    node = circle
    while True:
        if node.val == current_marble.val:
            print('(%d) ' % node.val, end='')
        else:
            print(node.val, ' ', end='')
        node = node.next_node
        if node == circle:
            break
    print(scores)

class Node:
    val = 0
    next_node = None
    prev_node = None
    
    def __init__(self, val):
        self.val = val
    
    def insertAfter(self, node):
        if node.next_node or node.prev_node:
            raise Exception()

        if self.next_node:
            self.next_node.prev_node = node
        node.next_node = self.next_node
        self.next_node = node
        node.prev_node = self

        return node
    
    def insertBefore(self, node):
        if node.next_node or node.prev_node:
            raise Exception()
        
        if self.prev_node:
            self.prev_node.next_node = node
        node.prev_node = self.prev_node
        self.prev_node = node
        node.next_node = self
        
        return node
    
    def pop(self):
        self.prev_node.next_node = self.next_node
        self.next_node.prev_node = self.prev_node
        return self.val
        
circle = Node(0)
circle.next_node = circle
circle.prev_node = circle

player_count = int(sys.argv[1])
last_marble = int(sys.argv[2])

scores = defaultdict(lambda: 0)
current_marble = circle
next_marble = 0
current_player = -1
# print_state(current_player, circle, current_marble, dict(scores))

while next_marble < last_marble:    
    next_marble += 1
    current_player = (current_player + 1) % player_count
    if next_marble % 23 == 0:
        scores[current_player] += next_marble
        for i in range(7):
            current_marble = current_marble.prev_node
        scores[current_player] += current_marble.pop()
        current_marble = current_marble.next_node

    else:
        current_marble = current_marble.next_node.insertAfter(Node(next_marble))
    # print_state(current_player, circle, current_marble, dict(scores))

print(max(scores.values()))