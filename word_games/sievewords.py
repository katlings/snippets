#!/usr/bin/env python3

"""
What is the longest word that does not contain the letters of any shorter word
in it?
"""

debug = False


def contains(word, s):
    # true if all letters of s are contained in word
    for letter in s:
        if letter in word:
            word = word.replace(letter, '', 1)
        else:
            return False
    return True


def contains_any(word, sieve):
    # true if all letters of any word in the sieve are contained in word
    for s in sieve:
        if contains(word, s):
            return s
    return False


if __name__ == '__main__':
    with open('scrabble-dictionary.txt', 'r') as f:
        words = f.readlines()
        words.append("a")
        words.append("I")

    sieve = []
    words.sort(key=lambda x: len(x))
    words = map(lambda x: x.strip().lower(), words)

    for word in words:
        if debug:
            print(word)
        s = contains_any(word, sieve)
        if not s:
            sieve.append(word)
            if debug:
                print(sieve)
        else:
            if debug:
                print("%s is contained in %s" % (s, word))

    print(sieve)
    print(sieve[-1])
