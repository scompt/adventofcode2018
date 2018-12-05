#!/usr/bin/env python3

import sys
from collections import defaultdict

inp = list(sys.stdin.readlines()[0].strip())
alphabet = set(''.join(sorted(inp)).upper())
inp1 = list(inp)
print(alphabet)

lens={}
for char in alphabet:
    inp = list(''.join(inp1).replace(char, '').replace(char.lower(), ''))
    
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
    lens[char] = len(inp)

min_len = min(lens.items(), key=lambda x: x[1])
print(min_len)