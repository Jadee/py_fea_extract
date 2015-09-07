#!/bin/bash

source ../../../conf/mine.conf
source ../../../conf/word2vec_task.conf

OUTPUT=$url_augmented_merge_pairs_path
if $HADOOP_BIN fs -test -e $OUTPUT
then
    $HADOOP_BIN fs -rmr $OUTPUT
fi
echo $OUTPUT

INPUT1="$url_augmented_by_query_path/*/part*"

# paras for hadoop
MAP_CAP=1500
REDUCE_CAP=1000
MAP_NUM_PER_NODE=5
REDUCE_NUM_PER_NODE=5
NUM_MAP=6000
NUM_REDUCE=1800

${HADOOP_BIN} streaming \
    -D stream.num.map.output.key.fields=2 \
    -D num.key.fields.for.partition=2 \
    -D mapred.job.name="merge_everyDay_pairs" \
    -D mapred.job.map.capacity=$MAP_CAP \
    -D mapred.job.reduce.capacity=$REDUCE_CAP \
    -D mapred.map.capacity.per.tasktracker=$MAP_NUM_PER_NODE \
    -D mapred.reduce.capacity.per.tasktracker=$REDUCE_NUM_PER_NODE \
    -D mapred.map.tasks=$NUM_MAP \
    -D mapred.reduce.tasks=$NUM_REDUCE \
    -input ${INPUT1}  \
    -output ${OUTPUT} \
    -mapper  "cat" \
    -reducer "$python merge_pairs.py" \
    -file  "./merge_pairs.py" \
    -cacheArchive $python_src \
    -partitioner "org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner" \
    -jobconf stream.memory.limit=2000 \
    -jobconf mapred.job.priority=$task_priority \

if [ $? -ne 0 ]; then
    echo "[FATAL]:hadoop failed!"
    exit 1
fi
