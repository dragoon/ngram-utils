#!/usr/bin/env python
"""Filters determiners and forms new n-grams with skips"""

import sys
import shelve
import anydbm
import nltk
import os

from kilogram.dataset.wikipedia.entities import parse_types_text

N = int(os.environ['NGRAM'])
if not N:
    print 'N is not specified'
    exit(0)

dbpedia_redirects = anydbm.open('dbpedia_redirects.dbm', 'r')
dbpedia_types = shelve.open('dbpedia_types.dbm', flag='r')


for line in sys.stdin:
    if not line:
        continue
    line = parse_types_text(line, dbpedia_redirects, dbpedia_types)
    sentences = line.split(' . ')
    last = len(sentences) - 1
    for i, sentence in enumerate(sentences):
        try:
            unicode(sentence)
        except UnicodeDecodeError:
            continue
        if i == last and not sentence.endswith('.'):
            continue
        if not sentence.endswith('.'):
            sentence += ' .'
        words = sentence.split()
        for n in range(1,N+1):
            for ngram in nltk.ngrams(words, n):
                ngram_joined = ' '.join(ngram)
                print '%s\t%s' % (ngram_joined, 1)

dbpedia_redirects.close()
dbpedia_types.close()