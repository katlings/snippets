#!/usr/bin/env python3

import bs4
from nltk.corpus import stopwords
import re
import requests
import textract


COMMON_WORDS = set(stopwords.words('english'))


def alphanum(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower())


def tally_words(word_list):
    tallies = {}
    for i, word in enumerate(word_list):
        if not word in tallies:
            tallies[word] = []
        tallies[word].append(i)
    return tallies


def fetch_script(url):
    response = requests.get(url)
    bs = bs4.BeautifulSoup(response.content, 'html.parser')
    script = bs.find('pre').get_text()
    return script


def clean_script(script):
    words = [alphanum(w) for w in script.split() if w != w.upper() and alphanum(w)]
    return words


def place_weight(locations, num_total_words):
    percentages = [l/num_total_words for l in locations]
    return sum(percentages)/len(percentages)


def sort_by_popularity(tallies):
    uses = [(len(locs), word) for word, locs in tallies.items() if word not in COMMON_WORDS]
    return sorted(uses, reverse=True)


def avengers():
    url = 'https://www.imsdb.com/scripts/Avengers,-The-(2012).html'
    script = fetch_script(url)
    words = clean_script(script)
    return words


def frozen():
    url = 'https://www.imsdb.com/scripts/Frozen-(Disney).html'
    script = fetch_script(url)
    words = clean_script(script)
    return words


def exorcist():
    script = textract.process('the-exorcist-1973.pdf').decode('utf-8')
    words = clean_script(script)
    return words


def cabin():
    script = textract.process('cabin-in-the-woods-2012.pdf').decode('utf-8')
    words = clean_script(script)
    return words


def heuristic(occurrences, num_words):
    if len(occurrences) <= 5:
        return 0
    return 0.2*len(occurrences) * (1 - place_weight(occurrences, num_words))**2


def main():
    words = cabin()
    tallies = tally_words(words)
#   popularity = sort_by_popularity(tallies)
#   print('Top 50 words')
#   for p in popularity[:50]:
#       print(p, place_weight(tallies[p[1]], len(words)))
    word_set = set(word for word in words if word and word not in COMMON_WORDS)
    ordered_words = sorted(word_set, key=lambda w: heuristic(tallies[w], len(words)), reverse=True)
    for word in ordered_words[:50]:
        locs = tallies[word]
        weight = place_weight(locs, len(words))
        h = heuristic(locs, len(words))
        print(word, len(locs), weight, h, sep='\t')


if __name__ == '__main__':
    main()
