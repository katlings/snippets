#!/usr/bin/env python

import unittest

from ss import ss, gifts, peeps, mutual_blacklist


class TestSecretSanta(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """ find an answer """
        cls.answer = ss(gifts, peeps, mutual_blacklist)
        while not cls.answer:
            cls.answer = ss(gifts, peeps, mutual_blacklist)
    
    def test_givers(self):
        """ make sure all people are giving items """
        self.assertItemsEqual(peeps, self.answer.keys())

    def test_givees(self):
        """ make sure all people are receiving the correct number of items """
        exchanges = {}
        for _, givees in self.answer.items():
            for givee in givees:
                if givee not in exchanges:
                    exchanges[givee] = 0
                exchanges[givee] += 1

        for peep in peeps:
            self.assertTrue(peep in exchanges)
            self.assertEqual(exchanges[peep], gifts)

    def test_mutual_blacklist(self):
        """ make sure the blacklist is mutual """
        for p1, ps in mutual_blacklist.items():
            for p2 in ps:
                self.assertIn(p2, mutual_blacklist[p1])

    def test_blacklist(self):
        """ make sure nobody's giving to a person they shouldn't be """
        for giver, givees in self.answer.items():
            for givee in givees:
                self.assertNotIn(givee, mutual_blacklist.get(giver, []))


if __name__ == "__main__":
    unittest.main()
