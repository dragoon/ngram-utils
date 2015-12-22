"""
spark-submit --master yarn-client --num-executors 20 --executor-memory 5g ./entity_linking/spark_candidate_ngrams.py "/user/roman/dbpedia_data.txt" "/user/roman/wiki_anchors" "/user/roman/candidate_ngram_links"
pig -p table=wiki_anchor_ngrams -p path=/user/roman/candidate_ngram_links ./hbase_upload_array.pig
"""
import sys
from pyspark import SparkContext
from itertools import combinations
from kilogram import ListPacker


sc = SparkContext(appName="CandidateEntityLinkings")


def generate_label_ngrams(line):
    result_labels = set()

    def proper_label(uri):
        # TODO: many urls start with '(', (79473)_1998_BX8, (R)-2-Methyl-CBS-oxazaborolidine
        label = uri.split(',', 1)[0].split('(', 1)[0]
        label = label.replace('_', ' ').strip()
        return label

    uri, types, redirects = line.split('\t')
    types = set(types.split(' '))
    label = proper_label(uri)
    if 'Person' in types:
        label = label.split()
        for i in range(1, len(label)+1):
            for ngram in combinations(label, i):
                result_labels.add(' '.join(ngram))
    else:
        result_labels.add(label)
    # add redirects
    for redirect in redirects.split():
        redirect_label = proper_label(redirect)
        if len(redirect_label) > 0:
            result_labels.add(redirect_label)

    return uri, result_labels

def uri_filter(line):
    uri = line.split('\t')[0]
    if '__' in uri:
        return False
    if uri.startswith('Template:'):
        return False
    if uri.startswith('List_of:'):
        return False
    return True


dbp_file = sys.argv[1]
uri_labels = sc.textFile(dbp_file).filter(uri_filter).map(generate_label_ngrams)


def map_uris(anchor_line):
    result = []
    _, uris = anchor_line.split('\t')
    for uri, v in ListPacker.unpack(uris):
        result.append((uri, long(v)))
    return result

anchors_file = sys.argv[2]
uri_counts = sc.textFile(anchors_file).flatMap(map_uris).reduceByKey(lambda x, y: x+y)


def generate_candidates(label_anchor):
    result = []
    uri, values = label_anchor
    labels, count = values
    if count is None:
        count = 1
    for label in labels:
        if len(label) > 0:
            result.append((label, (uri, count)))
    return result


def seqfunc(u, v):
    u.append(v)
    return u

def combfunc(u1, u2):
    u1.extend(u2)
    return u1

uri_label_counts = uri_labels.leftOuterJoin(uri_counts).flatMap(generate_candidates)\
    .aggregateByKey([], seqfunc, combfunc)


def map_anchors(anchor_line):
    label, uris = anchor_line.split('\t')
    result = []
    for uri, v in ListPacker.unpack(uris):
        result.append((uri, long(v)))
    return label, result

join = sc.textFile(anchors_file).map(map_anchors).fullOuterJoin(uri_label_counts)


def printer(value):
    label, values = value
    uri_counts_anchors, uri_count_labels = values
    if uri_count_labels is None:
        return label + '\t' + ListPacker.pack(uri_counts_anchors)
    elif uri_counts_anchors is None:
        return label + '\t' + ListPacker.pack(uri_count_labels)
    uri_count_labels_dict = dict(uri_count_labels)
    for uri, count in uri_counts_anchors:
        if uri not in uri_count_labels_dict:
            uri_count_labels_dict[uri] = count
    return label + '\t' + ListPacker.pack(uri_count_labels_dict.items())

join.map(printer).saveAsTextFile(sys.argv[3])
