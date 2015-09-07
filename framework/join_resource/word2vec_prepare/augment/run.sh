#!/bin/bash

source ../../../conf/mine.conf
source ../../../conf/word2vec_task.conf

if [ ! -n "$1" ]; then
    day_to_process=`date -d 'yesterday' +"%Y%m%d"`
else
    echo "para specified"
    day_to_process=$1
fi

echo "processing $day_to_process logs..."

# pc logs
INPUT1="$fcr_204/$day_to_process/*/part*"
INPUT2="$fcr_225/$day_to_process/*/part*"
INPUT3="$fcr_201/$day_to_process/*/part*"
# wise logs
INPUT4="$wise_222_223/$day_to_process/*/part*"

$HADOOP_BIN fs -test -e "$fcr_204/$day_to_process/"
if [ $? -ne 0 ]
then
    echo "no shitu_204 log"
    exit 0
fi

input_shitu_log_path=$INPUT1

$HADOOP_BIN fs -test -e "$fcr_225/$day_to_process/"
if [ $? -ne 0 ]
then
    echo "no shitu_225 log"
else
    input_shitu_log_path=$input_shitu_log_path" "$INPUT2
fi

$HADOOP_BIN fs -test -e "$fcr_201/$day_to_process/"
if [ $? -ne 0 ]
then
    echo "no shitu_201 log"
else
    input_shitu_log_path=$input_shitu_log_path" "$INPUT3
fi

$HADOOP_BIN fs -test -e "$wise_222_223/$day_to_process/"
if [ $? -ne 0 ]
then
    echo "no shitu_222_223 log"
else
    input_shitu_log_path=$input_shitu_log_path" "$INPUT4
fi

OUTPUT="$url_augmented_by_query_path/$day_to_process"
if $HADOOP_BIN fs -test -e $OUTPUT
then
    $HADOOP_BIN fs -rmr $OUTPUT
fi

# paras for hadoop
MAP_CAP=1500
REDUCE_CAP=200
MAP_NUM_PER_NODE=5
REDUCE_NUM_PER_NODE=5
NUM_MAP=2000
NUM_REDUCE=200

echo ${OUTPUT}

${HADOOP_BIN} streaming \
    -D stream.num.map.output.key.fields=2 \
    -D num.key.fields.for.partition=1 \
    -D mapred.job.name="augmentForLzf" \
    -D mapred.job.map.capacity=$MAP_CAP \
    -D mapred.job.reduce.capacity=$REDUCE_CAP \
    -D mapred.map.capacity.per.tasktracker=$MAP_NUM_PER_NODE \
    -D mapred.reduce.capacity.per.tasktracker=$REDUCE_NUM_PER_NODE \
    -D mapred.map.tasks=$NUM_MAP \
    -D mapred.reduce.tasks=$NUM_REDUCE \
    -D mapred.combine.input.format.local.only=false \
    -input  ${input_shitu_log_path}  \
    -output ${OUTPUT} \
    -mapper  "$python compute_mapper.py"  \
    -reducer "$python compute_reducer.py" \
    -file  "./compute_mapper.py"  \
    -file  "./compute_reducer.py" \
    -cacheArchive $python_src \
    -partitioner  "org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner" \
    -inputformat  "org.apache.hadoop.mapred.CombineTextInputFormat"  \
    -jobconf stream.memory.limit=2000 \
    -jobconf mapred.min.split.size=100000000 \
    -jobconf mapred.job.priority=$task_priority \
    
if [ $? -ne 0 ]; then
    echo "[FATAL]:hadoop failed!"
    exit 1
fi

