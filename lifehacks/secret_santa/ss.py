#!/usr/bin/env python

"""
Given a list of people, generate a Secret Santa scenario where every
participant gives n gifts to other participants and recieves n in return.
"""

import argparse
import random

import yagmail


gifts = 1

info = {
    'Alexa': 'redacted',
    'Ben Jones': 'redacted',
    'Bremmy': 'redacted',
    'Calvin': 'redacted',
    'Chelsea': 'redacted',
    'Eric': 'redacted',
    'Jack': 'redacted',
    'James': 'redacted',
    'Janis': 'redacted',
    'John': 'redacted',
    'Kate': 'redacted',
    'Kathryn': 'redacted',
    'Katharina': 'redacted',
    'Laura Grace': 'redacted',
    'Ryan': 'redacted',
    'Sandra': 'redacted',
}


# The following pairs of people should not be assigned to each other for
# whatever reason; maybe they're exchanging gifts independently or maybe they
# don't know each other well.
mutual_stoplist = [
    ('Calvin', 'Janis'),
    ('Kate', 'Sandra'),
    ('Chelsea', 'Ryan'),
    ('Eric', 'Katharina'),
    ('John', 'Laura Grace'),
    ('James', 'Jack'),
    ('James', 'Ben Jones'),
    ('James', 'Janis'),
    ('Jack', 'Ben Jones'),
    ('Jack', 'Janis'),
    ('Kathryn', 'Janis'),
]

# populate with last year's assignments to avoid double-punching
stoplist = {
    'Alexa': ['Chelsea'],
    'Ben Jones': ['Bremmy'],
    'Calvin': ['Kathryn'],
    'Chelsea': ['Janis'],
    'Eric': ['Laura Grace'],
    'Jack': ['Alexa'],
    'James': ['Kate'],
    'Janis': ['John'],
    'John': ['Jack'],
    'Kate': ['James'],
    'Kathryn': ['Eric'],
    'Katharina': ['Calvin'],
    'Laura Grace': ['Ryan'],
    'Ryan': ['Ben Jones'],
    'Sandra': ['Katharina'],
    'Bremmy': ['Sandra'],
}

for a, b in mutual_stoplist:
    if not a in stoplist:
        stoplist[a] = []
    if not b in stoplist:
        stoplist[b] = []
    stoplist[a].append(b)
    stoplist[b].append(a)


def check(giver, givee, other_givees, constraints):
    return giver != givee and givee not in other_givees and givee not in constraints.get(giver, [])


def ss(n, givers, constraints):
    givees = givers * n
    random.shuffle(givees)
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


email_text = """Dear {},

Happy Secret Santa 2022! You're giving a gift to {} this year, to be exchanged on January 7, 2023. Price target is $25, give or take. Check Discord for a wishlist links thread and post your own!

Happy holidays,
Santa's Helper
"""


def send_emails(assigns, dry_run=True):
    y = yagmail.SMTP('complikated@gmail.com', 'redacted')

    for assign, assignee in assigns.items():
        assignee = assignee[0]
        giver_email = info[assign]

        body = email_text.format(assign, assignee)

        if dry_run:
            print(body)
        else:
            y.send(
                to=giver_email,
                subject='Friendsmas Secret Santa 2022',
                contents=body,
            )



def run():
    parser = argparse.ArgumentParser(description='Generate a Secret Santa scenario for the input people')
    parser.add_argument('--num-gifts', '-n', type=int, default=gifts, help='The number of gifts each person should give and receive (default %d)' % gifts)
    parser.add_argument('--dry-run', '-d', action='store_true', help='A dry run will print emails instead of sending them')
    parser.add_argument('--go-mode', '-g', action='store_true', help='Send emails without confirming assignments')
    parser.add_argument('players', nargs='*', default=list(info.keys()), help='The players. Input all names separated by spaces')
    args = parser.parse_args()

    if len(args.players) <= args.num_gifts:
        print("At least %d people must be participating to exchange %d gifts" % (args.num_gifts + 1, args.num_gifts))
        return

    answer = ss(args.num_gifts, args.players, stoplist)
    while not answer:  # i.e. no solution was returned
        print("oops; rerunning")
        answer = ss(args.num_gifts, args.players, stoplist)

    if not args.go_mode:
        print(answer)

        go_ahead = input('Proceed to email? ')
        if go_ahead[0] in 'yY':
            send_emails(answer, args.dry_run)
        else:
            run()
    else:
        send_emails(answer, args.dry_run)


if __name__ == '__main__':
    run()
