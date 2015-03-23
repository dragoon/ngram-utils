#!/usr/bin/env python
"""Mapper to filter and extract types"""

import sys
from kilogram.ngram_service import SUBSTITUTION_TOKEN

for line in sys.stdin:
    # split the line into words
    ngram, num = line.strip().split('\t')

    type_count = ngram.count('<dbpedia:')
    if type_count == 1:
        ngram = ngram.split()
        type_index = [i for i, x in enumerate(ngram) if x.startswith('<dbpedia:')][0]
        entity_type = ngram[type_index]
        ngram[type_index] = SUBSTITUTION_TOKEN
        new_ngram = " ".join(ngram)
        print '%s\t%s\t%s' % (new_ngram, entity_type, num)
