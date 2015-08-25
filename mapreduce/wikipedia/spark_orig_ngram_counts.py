"""
spark-submit --master yarn-client ./wikipedia/spark_orig_ngram_counts.py "/user/roman/wikipedia_anchors_orig" "/user/roman/orig_ngram_counts"
"""
import sys
from pyspark import SparkContext


sc = SparkContext(appName="WikipediaAnchors")

lines = sc.textFile(sys.argv[1])

# Split each line into words
def unpack_achors(line):
    ngram, uri_list = line.split('\t')
    total_count = sum(int(x.rsplit(",", 1)[1]) for x in uri_list.split(" "))
    return ngram.replace(" ", "_"), total_count


def filter_ambiguous(line):
    ngram, uri_list = line.split('\t')
    uri_set = set(x.split(',')[0].lower() for x in uri_list.split(' '))
    if len(uri_set) == 1:
        return True
    return False


anchor_counts = lines.filter(filter_ambiguous).map(unpack_achors)


dbp_types_file = sc.textFile("/user/roman/dbpedia_types.txt")
dbp_types = dbp_types_file.map(lambda uri_types: (uri_types.split('\t')[0], 1)).distinct()
dbp_types_lower = dbp_types.map(lambda dbp_type: (dbp_type[0].lower(), dbp_type[0]))

type_anchors_join = dbp_types.join(anchor_counts)
types_anchors_lower_join = dbp_types_lower.join(anchor_counts)


def revert_lower_join(line):
    uri_lower, uri_count = line
    return uri_count


types_anchors_lower_join = types_anchors_lower_join.map(revert_lower_join)
type_anchors_join = type_anchors_join.map(lambda line: (line[0], line[1][1]))

type_anchors = type_anchors_join.join(types_anchors_lower_join)
type_anchors.map(lambda x: x[0]+'\t'+ str(x[1][0])+','+str(x[1][1])).saveAsTextFile(sys.argv[2])
