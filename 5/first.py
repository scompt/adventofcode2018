#!/usr/bin/env python3

import sys
from collections import defaultdict

inp = list(sys.stdin.readlines()[0].strip())

i=0
while i<len(inp)-1:
    a = inp[i]
    b = inp[i+1]
    if a!=b and a.upper()==b.upper():
        inp.pop(i)
        inp.pop(i)
        i=max(0, i-1)
    else:
        i+=1

print(len(inp))