#!/usr/bin/env python3

import sys

total = 0
for line in sys.stdin.readlines():
    total += int(line.strip())

print(total)