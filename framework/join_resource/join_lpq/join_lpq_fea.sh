#!/bin/bash

source ../../conf/mine.conf

echo $1,$2,$3,$4
INPUT1=$1"/part*"  #log  ‰»Î
INPUT2=$2"/part*"  #landing page Ãÿ’˜ ‰»Î
OUTPUT=$3          # ‰≥

HADOOP=$4
model_type=$5
${HADOOP} fs -rmr ${OUTPUT}

MAP_CAP=1500
REDUCE_CAP=1200
MAP_NUM_PER_NODE=5
REDUCE_NUM_PER_NODE=5

if [ $model_type == "predict" ]
then
    NUM_MAP=5000
    NUM_REDUCE=1200
else
    NUM_MAP=1000
    NUM_REDUCE=100
fi

echo ${OUTPUT}

${HADOOP} streaming \
    -D stream.num.map.output.key.fields=2 \
    -D num.key.fields.for.partition=1 \
    -input  ${INPUT1}  \
    -input  ${INPUT2}  \
    -output ${OUTPUT} \
    -mapper  "$python cat_fea_lpfea.py mapper af_parse.conf"  \
    -reducer "$python cat_fea_lpfea.py reduce af_parse.conf" \
    -file "./cat_fea_lpfea.py" \
    -file "../af_parse.conf" \
    -cacheArchive $python_src \
    -partitioner "org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner" \
    -jobconf mapred.job.name="join_lpq" \
    -jobconf mapred.job.map.capacity=$MAP_CAP \
    -jobconf mapred.job.reduce.capacity=$REDUCE_CAP \
    -jobconf mapred.map.capacity.per.tasktracker=$MAP_NUM_PER_NODE \
    -jobconf mapred.reduce.capacity.per.tasktracker=$REDUCE_NUM_PER_NODE \
    -jobconf mapred.map.tasks=$NUM_MAP \
    -jobconf mapred.reduce.tasks=$NUM_REDUCE \
    -jobconf mapred.min.split.size=100000000 \
    -jobconf stream.memory.limit=4000 \
    -jobconf mapred.job.priority=$task_priority \

if [ $? -ne 0 ]; then
    exit 1
fi

