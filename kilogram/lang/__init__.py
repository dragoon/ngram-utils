import re

DT_STRIPS = {'my', 'our', 'your', 'their', 'a', 'an', 'the', 'her', 'its', 'his'}
PUNCT_SET = set('[!(),.:;?/[\\]^`{|}]')

FLOAT_REGEX = r'(?:[1-9]\d*|0)(?:[\.,]\d+)?'

INT_RE = re.compile(r'^[1-9]\d*$')
PERCENT_RE = re.compile(r'\b\d{1,2}([\.,]\d{1,2})?\%(\s|$)')
NUM_RE = re.compile(FLOAT_REGEX)
TIME_RE1 = re.compile(r'\b\d{1,2}:\d{2}\b')
TIME_RE2 = re.compile(r'\b\d{1,2}(?:[:\.][0-5]\d)?(a\.m\.|p\.m\.|am|pm)(\s|$)')
# we need to separate square and volume, otherwise they will be mixed
VOL_RE = re.compile(r'\b{0}m3(\s|$)'.format(FLOAT_REGEX))  # often occurs in Google N-grams
SQ_RE = re.compile(r'\b{0}m2(\s|$)'.format(FLOAT_REGEX))

_RE_NUM_SUBS = [('<AREA>', SQ_RE), ('<VOL>', VOL_RE), ('<PERCENT>', PERCENT_RE),
                ('<TIME1>', TIME_RE1), ('<TIME2>', TIME_RE2), ('<INT>', INT_RE), ('<NUM>', NUM_RE)]


def number_replace(word):
    word1 = word
    for repl, regex in _RE_NUM_SUBS:
        word1 = regex.sub(repl, word)
        if word1 != word:
            break
    return word1

def strip_determiners(ngram):
    """
    :type ngram: unicode
    :return: n-gram with stripped determiners
    """
    ngram = ngram.split()
    dt_positions = [i for i, x in enumerate(ngram) if x.lower() in DT_STRIPS]
    new_ngram = [word for i, word in enumerate(ngram)
                 if i not in dt_positions or
                 (i+1 < len(ngram) and ngram[i+1] in PUNCT_SET)]
    return ' '.join(new_ngram)


def strip_adjectives(tokens, pos_tokens):
    """
    :type tokens: list
    :type pos_tokens: list
    :return: (tokens, pos_tokens) with stripped adjectives
    """
    new_tokens = []
    adj_tokens = []
    for token, pos_tag in zip(tokens, pos_tokens):
        if pos_tag.startswith(('JJ', 'CC')):
            adj_tokens.append((token, pos_tag))
            continue
        elif not pos_tag.startswith('NN') and adj_tokens:
            new_tokens.extend(adj_tokens)
            adj_tokens = []
        new_tokens.append((token, pos_tag))
    return zip(*new_tokens)
