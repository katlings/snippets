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
    'Alexa': 'alexa.keizur@gmail.com',
    'Ben Jones': 'gilgergoggle@gmail.com',
    'Bremmy': 'john.highwind@gmail.com',
    'Calvin': 'marvinx03@gmail.com',
    'Chelsea': 'chelzwa@gmail.com',
    'Eric': 'eric.alexander.mullen@gmail.com',
    'Jack': 'jkopakowski@gmail.com',
    'James': 'james@dogayer.com',
    'Janis': 'ravyn.selene@gmail.com',
    'John': 'jtgrasel@gmail.com',
    'Kate': 'kateevans1014@gmail.com',
    'Kathryn': 'complikated@gmail.com',
    'Katharina': 'ladyktob@gmail.com',
    'Laura Grace': 'lgbeckerman@gmail.com',
    'Ryan': 'rd.bahm@gmail.com',
    'Sandra': 'sandralspitzer@gmail.com',
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
]

# populate with last year's assignments to avoid double-punching
stoplist = {
    'Alexa': ['Kate'],
    'Ben Jones': ['Eric'],
    'Calvin': ['Sandra'],
    'Chelsea': ['Kathryn'],
    'Eric': ['Bremmy'],
    'John': ['Ryan'],
    'Kate': ['Katharina'],
    'Kathryn': ['Janis'],
    'Katharina': ['John'],
    'Ryan': ['Calvin'],
    'Sandra': ['Chelsea'],
    'Janis': ['Ben Jones'],
    'Bremmy': ['Alexa'],
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

Happy Secret Santa 2021! You're giving a gift to {} () this year, to be exchanged on January 9, 2022. Price target is $25, give or take. Check Discord thread for wishlist links and post your own!

Happy holidays,
Santa's Helper
"""


def send_emails(assigns):
    y = yagmail.SMTP('complikated@gmail.com')

    for assign, assignee in assigns.items():
        assignee = assignee[0]
        giver_email, wishlist = info[assign]

        body = email_text.format(assign, assignee)

        y.send(
            to=giver_email,
            subject='Friendsmas Secret Santa 2021',
            contents=body,
        )



def run():
    parser = argparse.ArgumentParser(description='Generate a Secret Santa scenario for the input people')
    parser.add_argument('--num-gifts', '-n', type=int, default=gifts, help='The number of gifts each person should give and receive (default %d)' % gifts)
    parser.add_argument('players', nargs='*', default=list(info.keys()), help='The players. Input all names separated by spaces')
    args = parser.parse_args()

    if len(args.players) <= args.num_gifts:
        print("At least %d people must be participating to exchange %d gifts" % (args.num_gifts + 1, args.num_gifts))
        return

    answer = ss(args.num_gifts, args.players, stoplist)
    while not answer:  # i.e. no solution was returned
        print("oops; rerunning")
        answer = ss(args.num_gifts, args.players, stoplist)

    print(answer)

    go_ahead = input('Proceed to email? ')
    if go_ahead[0] in 'yY':
        send_emails(answer)
    else:
        run()


if __name__ == '__main__':
    run()
