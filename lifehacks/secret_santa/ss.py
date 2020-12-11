#!/usr/bin/env python

"""
Given a list of people, generate a Secret Santa scenario where every
participant gives n gifts to other participants and recieves n in return.
"""

import argparse
import random


gifts = 1
peeps = ['Alexa',
         'Ben',
         'Bremmy',
         'Calvin',
         'Chelsea',
         'Eric',
         'Janis',
         'John',
         'Kate',
         'Kathryn',
         'Katharina',
         'Ryan',
         'Sandra']


# The following pairs of people should not be assigned to each other for
# whatever reason; maybe they're exchanging gifts independently or maybe they
# don't know each other well.
blacklist = [
    ('Calvin', 'Janis'),
    ('Kate', 'Sandra'),
    ('Chelsea', 'Ryan'),
    ('Eric', 'Katharina'),
]

mutual_blacklist = {}

for a, b in blacklist:
    if not a in mutual_blacklist:
        mutual_blacklist[a] = []
    if not b in mutual_blacklist:
        mutual_blacklist[b] = []
    mutual_blacklist[a].append(b)
    mutual_blacklist[b].append(a)


def check(giver, givee, other_givees, constraints):
    return giver != givee and givee not in other_givees and givee not in constraints.get(giver, [])


def ss(n, givers, constraints):
    givees = givers * n
    random.shuffle(givees)
    m = {}

    for giver in givers:
        m[giver] = []
        for p in range(n):
            givee = givees.pop()

            # Keep track of the number of times we try to find a givee for this
            # giver. It's possible that we might screw ourselves over by only
            # having the giver or someone they're already gifting to available,
            # so in that case, we need to know when we've run out of options to
            # cut our losses and try again. Backtracking would be a more
            # time-efficient option, but that's hard and this doesn't get run
            # at huge scale so whatever.
            tally = 0

            while not check(giver, givee, m[giver], constraints):
                if tally > len(givees):
                    # We've tried every givee that's left and none of them work
                    return None
                givees.insert(0, givee)  # back of the queue
                givee = givees.pop()
                tally += 1

            m[giver].append(givee)

    return m


def run():
    parser = argparse.ArgumentParser(description='Generate a Secret Santa scenario for the input people')
    parser.add_argument('--num-gifts', '-n', type=int, default=gifts, help='The number of gifts each person should give and receive (default %d)' % gifts)
    parser.add_argument('players', nargs='*', default=peeps, help='The players. Input all names separated by spaces')
    args = parser.parse_args()

    if len(args.players) <= args.num_gifts:
        print("At least %d people must be participating to exchange %d gifts" % (args.num_gifts + 1, args.num_gifts))
        return

    answer = ss(args.num_gifts, args.players, mutual_blacklist)
    while not answer:  # i.e. no solution was returned
        print("oops; rerunning")
        answer = ss(args.num_gifts, args.players, mutual_blacklist)

    print(answer)


if __name__ == '__main__':
    run()
