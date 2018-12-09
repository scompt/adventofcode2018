#!/usr/bin/env python3

import sys
from collections import defaultdict

def print_states(states):
    print('[-] (0)')
    for player_number, circle, current_marble, scores in states:
        print('[%d] ' % (player_number+1), end='')
        for marble in circle:
            if marble == current_marble:
                print('(%d) ' % marble, end='')
            else:
                print(marble, ' ', end='')
        print(scores)

player_count = int(sys.argv[1])
last_marble = int(sys.argv[2])

scores = defaultdict(lambda: 0)
states = [(0, [0,1], 1, {}), (1, [0,2,1], 2, {})]
circle = [0, 2, 1]
current_marble = 2
next_marble = 2
current_player = 2

while current_marble < last_marble:
    next_marble += 1
    marble_index = (circle.index(current_marble) + 2) % len(circle)
    
    if next_marble % 23 == 0:
        scores[current_player] += next_marble
        marble_index = (marble_index - 9) % len(circle)
        scores[current_player] += circle.pop(marble_index)
        current_marble = circle[marble_index]

    else:
        circle.insert(marble_index, next_marble)
        current_marble = next_marble

    # states.append((current_player, list(circle), current_marble, dict(scores)))
    current_player = (current_player + 1) % player_count


# print_states(states)
print(max(scores.values()))