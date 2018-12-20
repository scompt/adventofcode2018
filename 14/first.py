#!/usr/bin/env python3

from itertools import islice

def print_state(board, elf1, elf2):
    """
    >>> board = create_board(3, 7)
    >>> elf1 = board
    >>> elf2 = board.next_node
    >>> print_state(board, elf1, elf2)
    (3)[7]
    """
    for node in board:
        if node == elf1:
            print('(%d)' % node.val, end='')
        elif node == elf2:
            print('[%d]' % node.val, end='')
        else:
            print(' %d ' % node.val, end='')
    print()

def create_board(*args):
    """
    >>> create_board(5)
     5 
    >>> create_board(5, 6, 7)
     5  6  7 
    """
    initial = Node(args[0])
    initial.next_node = initial
    initial.prev_node = initial
    
    node = initial
    for i in args[1:]:
        node = node.insertAfter(Node(i))
        
    return initial

def step(board, elf1, elf2):
    """
    >>> board = create_board(3, 7)
    >>> elf1 = board
    >>> elf2 = board.next_node

    >>> elf1, elf2, last_added = step(board, elf1, elf2)
    >>> print_state(board, elf1, elf2)
    (3)[7] 1  0 
    >>> last_added
    2

    >>> elf1, elf2, last_added = step(board, elf1, elf2)
    >>> print_state(board, elf1, elf2)
     3  7  1 [0](1) 0 
    >>> last_added
    2
    """
    added = 0
    prev_last = board.prev_node
    new_recipes = (int(c) for c in str(elf1.val + elf2.val))
    for c in new_recipes:
        added += 1
        board.insertBefore(Node(c))
    
    for i in range(1 + elf1.val):
        elf1 = elf1.next_node
    for i in range(1 + elf2.val):
        elf2 = elf2.next_node
    
    return (elf1, elf2, added)

def gogogo(board, elf1, elf2, round_count, last_recipes = 10):
    """
    >>> board = create_board(3, 7)
    >>> elf1 = board
    >>> elf2 = board.next_node    
    >>> gogogo(board, elf1, elf2, 9)
    '5158916779'

    >>> board = create_board(3, 7)
    >>> elf1 = board
    >>> elf2 = board.next_node
    >>> gogogo(board, elf1, elf2, 5)
    '0124515891'
    
    >>> board = create_board(3, 7)
    >>> elf1 = board
    >>> elf2 = board.next_node
    >>> gogogo(board, elf1, elf2, 2018)
    '5941429882'
    """
    added = 2
    while added < round_count + last_recipes:
        # print_state(board, elf1, elf2)
        elf1, elf2, last_added = step(board, elf1, elf2)
        added += last_added
    
    # print_state(board, elf1, elf2)

    if last_added == 2:
        return ''.join(reversed([str(node.val) for node in islice(reversed(board), last_recipes + 1)]))[:-1]
    else:
        return ''.join(reversed([str(node.val) for node in islice(reversed(board), last_recipes)]))
        
    

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
    
    def __repr__(self):
        return ''.join(' %d ' % node.val for node in self)
    
    def __iter__(self):
        node = self
        while True:
            yield node
            node = node.next_node
            if node == self:
                break
        
    def __reversed__(self):
        node = self.prev_node
        while True:
            yield node
            node = node.prev_node
            if node == self.prev_node:
                break
        
import sys

if len(sys.argv) == 2:
    inp = int(sys.argv[1])
    board = create_board(3, 7)
    elf1 = board
    elf2 = board.next_node
    print(gogogo(board, elf1, elf2, inp))

else:
    import doctest
    doctest.testmod(verbose = True)
