#!/usr/bin/env python3

import sys
from textwrap import dedent
from itertools import product, chain, islice, zip_longest, count
import heapq
from io import StringIO
from collections import defaultdict, namedtuple
import os.path
import math
import types
import copy

OPS = ['addr', 'addi', 'mulr', 'muli', 'banr', 'bani', 'borr', 'bori',
       'setr', 'seti', 'gtir', 'gtri', 'gtrr', 'eqri', 'eqir', 'eqrr']

class Computer(object):
  def __init__(self, A=0, B=0, C=0, D=0, opcode_mapping=None):
    self.registers = [A, B, C, D]
    self.opcode_mapping = opcode_mapping
  
  def __repr__(self):
    """
    >>> c = Computer()
    >>> c
    Computer[0, 0, 0, 0]
    >>> c = Computer(1, 2, 3, 4)
    >>> c
    Computer[1, 2, 3, 4]
    """
    return 'Computer%s' % self.registers
  
  def __eq__(self, other):
    """
    >>> Computer() == Computer()
    True
    >>> Computer(1, 2, 3, 4) == Computer(1, 2, 3, 4)
    True
    >>> Computer(1, 2, 3, 4) == Computer()
    False
    """
    return self.registers == other.registers
  
  def addr(self, A, B, C):
    self.registers[C] = self.registers[A] + self.registers[B]
  
  def addi(self, A, B, C):
    self.registers[C] = self.registers[A] + B
  
  def mulr(self, A, B, C):
    self.registers[C] = self.registers[A] * self.registers[B]
  
  def muli(self, A, B, C):
    self.registers[C] = self.registers[A] * B
  
  def banr(self, A, B, C):
    self.registers[C] = self.registers[A] & self.registers[B]
  
  def bani(self, A, B, C):
    self.registers[C] = self.registers[A] & B
  
  def borr(self, A, B, C):
    self.registers[C] = self.registers[A] | self.registers[B]
  
  def bori(self, A, B, C):
    self.registers[C] = self.registers[A] | B
  
  def setr(self, A, _, C):
    self.registers[C] = self.registers[A]
  
  def seti(self, A, _, C):
    self.registers[C] = A

  def gtir(self, A, B, C):
    self.registers[C] = int(A > self.registers[B])
  
  def gtri(self, A, B, C):
    self.registers[C] = int(self.registers[A] > B)
  
  def gtrr(self, A, B, C):
    self.registers[C] = int(self.registers[A] > self.registers[B])
  
  def eqir(self, A, B, C):
    self.registers[C] = int(A == self.registers[B])
  
  def eqri(self, A, B, C):
    self.registers[C] = int(self.registers[A] == B)
  
  def eqrr(self, A, B, C):
    self.registers[C] = int(self.registers[A] == self.registers[B])
  
  def execute(self, op, A, B, C):
    op_name = self.opcode_mapping[op]
    operation = getattr(self, op_name)
    operation.__call__(A, B, C)

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    pass

def grouplen(l, n):
  'https://stackoverflow.com/a/312464/111777'
  return [l[i:i + n] for i in range(0, len(l), n)]

def computer_from(blah):
  """
  >>> computer_from('Before: [1, 0, 2, 0]')
  Computer[1, 0, 2, 0]
  """
  numbers = blah.partition(':')[2].lstrip()
  return Computer(*(int(b) for b in numbers[1:-1].split(', ')))

def parse(stream):
  """
  >>> inp = r'''
  ... Before: [1, 0, 2, 0]
  ... 4 1 0 1
  ... After:  [1, 1, 2, 0]
  ... 
  ... Before: [2, 3, 1, 2]
  ... 2 1 0 1
  ... After:  [2, 1, 1, 2]
  ... 
  ... f'''
  >>> samples, _ = parse(StringIO(dedent(inp).strip()))
  >>> samples
  [(Computer[1, 0, 2, 0], [4, 1, 0, 1], Computer[1, 1, 2, 0]), (Computer[2, 3, 1, 2], [2, 1, 0, 1], Computer[2, 1, 1, 2])]
  
  >>> inp = r'''
  ... Before: [2, 0, 1, 0]
  ... 11 1 0 2
  ... After:  [2, 0, 1, 0]
  ... 
  ... 
  ... 
  ... 9 3 3 0
  ... 9 1 0 1
  ... 9 0 1 2
  ... 3 1 2 2
  ... '''
  >>> samples, _ = parse(StringIO(dedent(inp).strip()))
  >>> samples
  [(Computer[2, 0, 1, 0], [11, 1, 0, 2], Computer[2, 0, 1, 0])]
  """
  lines = [l.strip() for l in stream.readlines()]
  groups = grouplen(lines, 4)
  samples = []
  for i, group in enumerate(groups):
    if len(group) != 4: break
    if group[0] == '': break
    
    before, operation, after, _ = group

    before = computer_from(before)
    operation = [int(b) for b in operation.split(' ')]
    after = computer_from(after)

    samples.append((before, operation, after))
  
  program = []
  for op in lines[(i*4)+2:]:
    program.append([int(b) for b in op.split(' ')])
    
  return (samples, program)

def blah(samples):
  """
  >>> samples = [(Computer(1, 0, 2, 0), [4, 1, 0, 1], Computer(1, 1, 2, 0)), (Computer(2, 3, 1, 2), [2, 1, 0, 1], Computer(2, 1, 1, 2))]
  >>> blah(samples, 3)
  1
  """
  possibilities = defaultdict(lambda: set())  
  for initial_before, operation_parameters, after in samples:
    for operation_name in OPS:
      before = copy.deepcopy(initial_before)
      operation = getattr(before, operation_name)
      operation.__call__(*operation_parameters[1:])
      
      if before == after:
        possibilities[operation_parameters[0]].add(operation_name)

  solved = set()
  opcodes = [None] * len(OPS)
  while not len(solved) == len(OPS):
    for op_number, opcode_possibilities in possibilities.items():
      opcode_possibilities.difference_update(solved)
      
      if len(opcode_possibilities) == 1:
        operation_name = list(opcode_possibilities)[0]      
        if opcodes[op_number] and not opcodes[op_number] == operation_name:
          assert False
        opcodes[op_number] = operation_name
        solved.add(operation_name)

  return opcodes
    
if len(sys.argv) == 2 and os.path.isfile(sys.argv[1]):
  samples, program = parse(open(sys.argv[1]))
  mapping = blah(samples)

  c = Computer(opcode_mapping = mapping)
  for op in program:
    c.execute(*op)
  print(c)

else:
  import doctest
  doctest.testmod(verbose=True)
