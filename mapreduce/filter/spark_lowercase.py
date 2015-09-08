"""
spark-submit --num-executors 20 --master yarn-client ./filter/spark_lowercase.py "/user/roman/wikipedia_ngrams" "/user/roman/ngram_counts"
"""
import sys
from pyspark import SparkContext


sc = SparkContext(appName="WikipediaLowercase")

lines = sc.textFile(sys.argv[1])


# Split each line into words
def label_num(line):
    ngram, num = line.split('\t')
    return ngram.replace(' ', '_'), int(num)

ngram_counts = lines.map(label_num)

dbp_types = sc.textFile("/user/roman/dbpedia_types.txt").map(lambda line: (line.split('\t')[0], 1)).distinct()
dbp_lowercase = sc.textFile("/user/roman/dbpedia_lowercase2labels.txt").map(lambda line: line.split('\t'))

ngram_counts_join = ngram_counts.join(dbp_types).map(lambda x: (x[0], x[1][0]))
ngram_counts_lower_join = ngram_counts.join(dbp_lowercase).map(lambda x: (x[1][1], x[1][0]))

result = ngram_counts_lower_join.fullOuterJoin(ngram_counts_join)

result.map(lambda x: x[0]+'\t'+str(x[1][0] or 0)+','+str(x[1][1] or 0)).saveAsTextFile(sys.argv[2])
