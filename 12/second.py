#!/usr/bin/env python3

import sys
from collections import defaultdict
from itertools import dropwhile

RULE_SIZE=5
RULE_MIDDLE_OFFSET=2
ROUND_COUNT=20

WOOT = 2**RULE_SIZE-1

def print_state(state):
  min_index = min(state.keys())
  max_index = max(state.keys())
  
  for i in range(min_index, max_index):
    print(state[i], end='')
  print()

def print_state2(state):
  print(bin(state)[2:].replace('0', '.').replace('1', '#'))
  
def step(state, rules):
  min_index = min(state.keys())
  max_index = max(state.keys())
  new_state = defaultdict(lambda: '.')

  for i in range(min_index-RULE_SIZE, max_index+1+RULE_SIZE):
    for r in rules.items():
      if all(state[i+j]==r[0][j] for j in range(RULE_SIZE)):
        new_state[i+RULE_MIDDLE_OFFSET] = r[1]
        break
  
  return new_state

def step2(state, rules):
  new_state = 0
  for i in range(state.bit_length()+RULE_SIZE):
    pattern = (state << RULE_SIZE >> i) & WOOT
    val = rules[pattern]
    if val:
      new_state += (1 << i)

  while new_state&1 == 0:
    new_state=new_state>>1
  return new_state

def parse_initial(lines):
  state = defaultdict(lambda: '.')
  for i, p in enumerate(lines[0][15:]):
    state[i] = p
  return state

def parse_initial2(lines):
  state = int(lines[0][15:].replace('.', '0').replace('#', '1'), 2)
  return state

def parse_rules(lines):  
  return defaultdict(lambda: '.', dict([r.split(' => ') for r in lines[2:]]))

def parse_rules2(lines):  
  raw_rules = defaultdict(lambda: '.', dict([r.split(' => ') for r in lines[2:]]))
  rules=[False] * (2**RULE_SIZE)
  for rule,val in raw_rules.items():
    rules[int(rule.replace('.', '0').replace('#', '1'), 2)] = val == '#'
  return rules

def show_sum(state):
  return sum(k for k,v in state.items() if v == '#')

def show_sum2(state):
  print(sum(i for i, bit in enumerate(bin(state)[2:]) if bit == '1'))

lines = [l.strip() for l in sys.stdin.readlines()]

state = parse_initial(lines)
rules = parse_rules(lines)

last = 0
for i in range(100):
  this = show_sum(state)
  print('%d %d %d' % (i, this - last, this))
  last = this
  # print('%d %d' % (i, show_sum(state)))
  # print_state(state)
  state = step(state, rules)
# show_sum(state)
