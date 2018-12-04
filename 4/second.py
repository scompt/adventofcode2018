#!/usr/bin/env python3

import sys
from collections import defaultdict

SHIFT_START = 0
FALL_ASLEEP = 1
WAKE_UP     = 2
NOTHING     = 3

def parse(line):
    part = line[1:].partition('-')
    year = int(part[0])

    part = part[2].partition('-')
    month = int(part[0])
    
    part = part[2].partition(' ')
    day = int(part[0])
    
    part = part[2].partition(':')
    hour = int(part[0])

    part = part[2].partition('] ')
    minute = int(part[0])
    
    action = part[2][0:5]
    if action == 'Guard':
        action = (SHIFT_START, int(part[2][7:].partition(' ')[0]))
    elif action == 'falls':
        action = (FALL_ASLEEP, None)
    elif action == 'wakes':
        action = (WAKE_UP, None)
    else:
        sys.exit()
    
    sort_key = '%04d%02d%02d%02d%02d%1d' % (year, month, day, hour, minute, action[0])
    blah_key = '%04d%02d%02d%02d' % (year, month, day, hour)
    return (sort_key, year, month, day, hour, minute, action, blah_key)

def print_blah(asdf):
    for guard, schedule in asdf.items():
        print('%s #%4d ' % (guard[0][4:8], guard[1]), end='')
        for minute in schedule:
            if minute:
                print('#', end='')
            else:
                print('.', end='')
        print()

events = sorted((parse(line.strip()) for line in sys.stdin.readlines()), key=lambda x: x[0])

days=defaultdict(lambda: [NOTHING]*60)
for event in events:
    if event[6][0] == SHIFT_START:
        current_guard = event[6][1]
    elif event[6][0] == FALL_ASLEEP:
        days[(event[7], current_guard)][event[5]] = FALL_ASLEEP
    elif event[6][0] == WAKE_UP:
        days[(event[7], current_guard)][event[5]] = WAKE_UP

sleeptime=defaultdict(lambda: 0)
for (key, minutes) in days.items():
    start = 0
    total = 0
    while FALL_ASLEEP in minutes[start:]:
        total += minutes.index(WAKE_UP, start) - minutes.index(FALL_ASLEEP, start)
        start = minutes.index(WAKE_UP, start)+1
    sleeptime[key[1]] += total

asdf={}
for day in days.items():
    # print(day[1])
    blah = [False] * 60
    sleeping = False
    for index, state in enumerate(day[1]):
        if state == FALL_ASLEEP:
            sleeping = True
            blah[index] = True
        elif state == WAKE_UP:
            sleeping = False
        elif sleeping:
            blah[index] = True
    asdf[day[0]] = blah

all_guards=set(sleeptime.keys())

guard_minutes=defaultdict(lambda: [0]*60)
for guard, day in asdf.items():
    for minute in range(60):
        if day[minute]:
            guard_minutes[guard[1]][minute] += 1

guard_maxes = {}
for guard, val in guard_minutes.items():
    guard_maxes[guard] = max(val)

max_guard = max(guard_maxes, key=lambda x: guard_maxes[x])
max_minute = guard_minutes[max_guard]
print(max_guard * max_minute.index(guard_maxes[max_guard]))
