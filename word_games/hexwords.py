#!/usr/bin/env python3

"""
Allowing 1337speak hax, which words can be represented entirely in hex?
"""

# leetspeak: 1=I=l 5=S 9=g 0=O
# lesser leetspeak: 4=h 7=L 
letters = 'abcdefilsgo'


with open('/usr/share/dict/words', 'r') as f:
    words = f.readlines()
    
print([word.strip() for word in words if all(letter in letters for letter in word.strip())])
