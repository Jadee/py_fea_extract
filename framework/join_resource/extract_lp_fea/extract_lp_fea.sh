#!/bin/bash

source ../../conf/mine.conf

HADOOP=$1

INPUT1=$2
INPUT2=$3
INPUT3=$4
OUTPUT=$my_hadoop_path"/badcase/model/lpq_tmp"

${HADOOP} fs -rmr ${OUTPUT}

MAP_CAP=1500
REDUCE_CAP=1000
MAP_NUM_PER_NODE=3
REDUCE_NUM_PER_NODE=3
NUM_MAP=5000
NUM_REDUCE=1500

echo ${OUTPUT}

${HADOOP} streaming \
    -D stream.num.map.output.key.fields=2 \
    -D num.key.fields.for.partition=1 \
    -input  ${INPUT1}  \
    -input  ${INPUT2}  \
    -input  ${INPUT3}  \
    -output ${OUTPUT}  \
    -mapper  "export PYTHONIOENCODING=GB18030 && export LANG=zh_CN.gb2312:en_US.UTF-8:zh_CN.UTF-8:en_US && $python cat_lp_fea.py mapper af_parse.conf"  \
    -reducer "export PYTHONIOENCODING=GB18030 && export LANG=zh_CN.gb2312:en_US.UTF-8:zh_CN.UTF-8:en_US && $python cat_lp_fea.py reduce"  \
    -file  "./cat_lp_fea.py" \
    -file  "./conf.py" \
    -file  "./process_str.py" \
    -file  "../af_parse.conf" \
    -cacheFile "$wildword_conf/pc_wise_url_pair#pc_wise_url_pair"  \
    -cacheArchive $python_src \
    -outputformat "org.apache.hadoop.mapred.lib.SuffixMultipleTextOutputFormat" \
    -partitioner  "org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner" \
    -jobconf mapred.job.name="json_decode_job" \
    -jobconf mapred.job.map.capacity=$MAP_CAP \
    -jobconf mapred.job.reduce.capacity=$REDUCE_CAP \
    -jobconf mapred.map.capacity.per.tasktracker=$MAP_NUM_PER_NODE \
    -jobconf mapred.reduce.capacity.per.tasktracker=$REDUCE_NUM_PER_NODE \
    -jobconf mapred.map.tasks=$NUM_MAP \
    -jobconf mapred.reduce.tasks=$NUM_REDUCE \
    -jobconf mapred.job.priority=$task_priority \
    -jobconf stream.memory.limit=8000

if [ $? -ne 0 ]; then
    exit 1
fi

$HADOOP_BIN fs -rmr $5
$HADOOP_BIN fs -mv ${OUTPUT} $5
if [[ $? -ne 0 ]]    #½Å±¾Ö´ÐÐ²»³É¹¦ Ö±½Ó·µ»Ø
then
    echo "mv lpq failed"
    exit 1
fi

