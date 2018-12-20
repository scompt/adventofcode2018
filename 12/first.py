#!/usr/bin/env python3

import sys
from collections import defaultdict

RULE_SIZE=5
RULE_MIDDLE_OFFSET=2
ROUND_COUNT=20

WOOT = 2**RULE_SIZE-1

def print_state(state):
  print(bin(state)[2:].replace('0', '.').replace('1', '#'))

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

state = defaultdict(lambda: '.')
lines = [l.strip() for l in sys.stdin.readlines()]
state = int(lines[0][15:].replace('.', '0').replace('#', '1'), 2)
# print(state)
for index,char in enumerate(initial):
  state[index] = char == '#'
raw_rules = defaultdict(lambda: '.', dict([r.split(' => ') for r in lines[2:]]))
rules=[False] * (2**RULE_SIZE)
for rule,val in raw_rules.items():
  rules[int(rule.replace('.', '0').replace('#', '1'), 2)] = val == '#'
# print(rules)

print_state(state)
for i in range(ROUND_COUNT):
  # print(i)
  state = step(state, rules)
  # print_state(state)

# print(state)
print(sum(i for i, bit in enumerate(bin(state)[2:]) if bit == '1'))