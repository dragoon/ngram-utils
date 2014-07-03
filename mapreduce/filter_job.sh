#!/bin/bash

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
N=0
REDUCERS=20

while getopts "rn:" opt; do
    case "$opt" in
    n)  N=$OPTARG
        ;;
    r)  REDUCERS=$OPTARG
        ;;
    esac
done

shift $((OPTIND-1))

[ "$1" = "--" ] && shift

echo $1
echo $2
exit

hadoop fs -rm -r $2
cp ../extra/preps.txt words.txt
hadoop jar /opt/cloudera/parcels/CDH/lib/hadoop-mapreduce/hadoop-streaming.jar \
  -Dmapreduce.framework.name=yarn \
  -Dmapreduce.job.contract=false \
  -Dmapreduce.job.reduces=$REDUCERS \
  -cmdenv NGRAM=$N
  -files filter/mapper_filter.py,reducer_generic.py,words.txt \
  -mapper filter/mapper_filter.py \
  -reducer reducer_generic.py \
  -input $1 -output $2
rm words.txt