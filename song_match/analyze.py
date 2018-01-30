#!/usr/bin/env python3

import click
from nltk.corpus import cmudict
d = cmudict.dict()


def count_vowel_groups(word):
    # this is a first order approximation of number of syllables.
    # it won't be correct on  e.g. aria, Julia, praying, antiestablishment
    vowels = 'aeiouy'
    syllables = 0
    last_seen_consonant = True
    for letter in word:
        if letter not in vowels:
            last_seen_consonant = True
        else:
            syllables += last_seen_consonant
            last_seen_consonant = False
    # special case for last silent e
    if len(word) >= 2 and word[-1] == 'e' and word[-2] not in vowels:
        syllables -= 1
    return syllables


def get_syllable_stress(word):
    word = word.lower().strip()
    stresses_options = set()

    # special case for e.g. singin', prayin'. a common transcription in written lyrics
    # does not work on goin' as goin is apparently a word
    if not word in d and word.endswith('in') and word + 'g' in d:
        word = word + 'g'

    if not word in d:
        # try all combinations of syllables. why not?
        syllables = count_vowel_groups(word)
        for i in range(2**syllables):
            pattern = format(i, 'b').zfill(syllables)
            if pattern == '11' or not '11' in pattern:  # filter out two stresses in a row - it's rare at best
                stresses_options.add(pattern)
    else:
        pronunciations = d[word]
        for p in pronunciations:
            stress = []
            for syllable in p:
                if '1' in syllable or '2' in syllable:  # for now, ignore whatever 2 means
                    stress.append('1')
                if '0' in syllable:
                    stress.append('0')  # todo: watch for two unstressed in a row
                                        # ^ wtf self, what does this mean
            stresses_options.add(''.join(stress))

    return stresses_options


def fingerprint(word):
    stresses = get_syllable_stress(word)
    if not stresses:
        raise ValueError(f'Found no options for word {word}')
    if len(stresses) == 1:
        return stresses.pop()
    syllables = len(list(stresses)[0])
    if not all(len(s) == syllables for s in stresses):
        print('well crud we have to deal with multiple syllables here')
        return stresses.pop()  # lol pick one. TODO
    fp = []
    for i in range(syllables):
        if all(s[i] == '1' for s in stresses):
            fp.append('1')
        elif all(s[i] == '0' for s in stresses):
            fp.append('0')
        else:
            fp.append('x')
    return ''.join(fp)


def get_sequence_fingerprint(sequence):
    words = sequence.split()
    fps = []
    for word in words:
        fps.append(fingerprint(word))
    return ''.join(fps)


# hash a bunch of lyrics into sequence stress and use that to fetch similar ones
# potential optimization: mask all generated stresses for the important ones (but have to deal with different lengths)
# it may work to be generous on one-syllable stressing


@click.command()
@click.argument('filename')
def main(filename):
    try:
        with open(filename) as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = [filename]

    for line in lines:
        print(get_sequence_fingerprint(line))


if __name__ == '__main__':
    main()
