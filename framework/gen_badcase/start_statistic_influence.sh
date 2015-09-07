#!/bin/bash

source ../conf/mine.conf

INPUT0=$fcrview_201_path
INPUT1=$fcrview_204_path
INPUT2=$fcrview_225_path
INPUT3=$wiseview_path

INPUT4=$my_hadoop_path"/badcase/model/ba_temp/part*C"

OUTPUT=$sta_influence_out
HADOOP=$HADOOP_BIN

${HADOOP} fs -rmr ${OUTPUT}

MAP_CAP=1500
REDUCE_CAP=800
MAP_NUM_PER_NODE=5
REDUCE_NUM_PER_NODE=5
NUM_MAP=3000
NUM_REDUCE=1

echo ${OUTPUT}

${HADOOP} streaming \
    -D stream.num.map.output.key.fields=1 \
    -D num.key.fields.for.partition=1 \
    -D mapred.combine.input.format.local.only=false \
    -input  ${INPUT4}  \
    -output ${OUTPUT} \
    -mapper  "$python statistic_influence.py mapper delta_winfoid" \
    -reducer "$python statistic_influence.py reduce" \
    -file "./statistic_influence.py" \
    -file "./$today/delta_winfoid"  \
    -cacheArchive $python_src \
    -inputformat  "org.apache.hadoop.mapred.CombineTextInputFormat"  \
    -partitioner "org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner" \
    -jobconf mapred.job.name="badcase_gen_badcase" \
    -jobconf mapred.job.map.capacity=$MAP_CAP \
    -jobconf mapred.job.reduce.capacity=$REDUCE_CAP \
    -jobconf mapred.map.capacity.per.tasktracker=$MAP_NUM_PER_NODE \
    -jobconf mapred.reduce.capacity.per.tasktracker=$REDUCE_NUM_PER_NODE \
    -jobconf mapred.map.tasks=$NUM_MAP \
    -jobconf mapred.reduce.tasks=$NUM_REDUCE \
    -jobconf mapred.min.split.size=100000000 \
    -jobconf mapred.job.priority=$task_priority \

if [ $? -ne 0 ]; then
    exit 1
fi

${HADOOP} fs -getmerge $sta_influence_out $today/sta_influence
if [ $? -ne 0 ]; then
    echo "get influence failed"
    exit 1
fi
