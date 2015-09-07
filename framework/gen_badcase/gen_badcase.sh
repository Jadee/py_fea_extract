#!/bin/bash

source ../conf/mine.conf

#INPUT1="/app/ecom/fcr/lizhangfeng/badcase/model/predict_out/20131105/part-*"
#OUTPUT="/app/ecom/fcr/lizhangfeng/badcase/model/gen_badcase"

INPUT1=$predict_output_path/part*A
OUTPUT=$gen_badcase_out

echo ${INPUT1}

HADOOP=$HADOOP_BIN

${HADOOP} fs -rmr ${OUTPUT}

MAP_CAP=1500
REDUCE_CAP=800
MAP_NUM_PER_NODE=5
REDUCE_NUM_PER_NODE=5
NUM_MAP=1500
NUM_REDUCE=5

echo ${OUTPUT}

${HADOOP} streaming \
    -D stream.num.map.output.key.fields=1 \
    -D num.key.fields.for.partition=1 \
    -D abaci.split.optimize.enable=false \
    -input  ${INPUT1}  \
    -output ${OUTPUT} \
    -mapper  "$python gen_badcase.py af_parse.conf rule.conf"  \
    -reducer "cat" \
    -file "./gen_badcase.py" \
    -file "./acMatching.py"  \
    -file "../conf/af_parse.conf"  \
    -file "../conf/rule.conf"      \
    -file "../conf/famous_people_dict"  \
    -file "../conf/sex_term_dict"   \
    -file "../conf/user_bidword_trade.dict"  \
    -file "../conf/lose_weight_dict"  \
    -file "../conf/video_dict.txt"    \
    -file "../conf/video_whitelist.txt" \
    -cacheArchive $python_src \
    -partitioner "org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner" \
    -jobconf mapred.job.name="badcase_gen_badcase" \
    -jobconf mapred.job.map.capacity=$MAP_CAP \
    -jobconf mapred.job.reduce.capacity=$REDUCE_CAP \
    -jobconf mapred.map.capacity.per.tasktracker=$MAP_NUM_PER_NODE \
    -jobconf mapred.reduce.capacity.per.tasktracker=$REDUCE_NUM_PER_NODE \
    -jobconf mapred.map.tasks=$NUM_MAP \
    -jobconf mapred.reduce.tasks=$NUM_REDUCE \
    -jobconf mapred.min.split.size=20000000 \
    -jobconf mapred.job.priority=$task_priority \

if [ $? -ne 0 ]; then
    exit 1
fi

