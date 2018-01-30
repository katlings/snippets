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
    if not word in d and word.endswith('in') and word + 'g' in d:
        word = word + 'g'

    if not word in d:
        # try all combinations of syllables. why not?
        syllables = count_vowel_groups(word)
        for i in range(2**syllables):
            pattern = format(i, 'b').zfill(syllables)
            if pattern == '11' or not '11' in pattern:  # filter out two stresses in a row - it's rare!
                stresses_options.add(pattern)
    else:
        pronunciations = d[word]
        for p in pronunciations:
            stress = ''
            for syllable in p:
                if '1' in syllable or '2' in syllable:  # for now, ignore 2
                    stress = stress + '1'
                if '0' in syllable:
                    stress = stress + '0'  # todo: watch for two unstressed in a row
            stresses_options.add(stress)

    return stresses_options


def get_sequence_stress(sequence):
    words = sequence.split()
    stresses = ['']
    for word in words:
        word_stresses = get_syllable_stress(word)
        stresses = [s + ws for s in stresses for ws in word_stresses]
    return stresses


# hash a bunch of lyrics into sequence stress and use that to fetch similar ones
# potential optimization: mask all generated stresses for the important ones (but have to deal with different lengths)
# it may work to be generous on one-syllable stressing


@click.command()
@click.argument('sequence')
def main(sequence):
    print(get_sequence_stress(sequence))


if __name__ == '__main__':
    main()
