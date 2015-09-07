#!/bin/bash
source ../../conf/mine.conf
source ../../conf/word2vec_task.conf

if [ ! -n "$1" ]; then
    day_to_process=`date -d"2 day ago" +"%Y%m%d"`
else
    echo "para specified"
    day_to_process=$today
fi

echo "processing $day_to_process logs..."

# logs
INPUT1="$new_cookie_sort/$day_to_process/$input_pattern"
OUTPUT="${video_resource_path}"

$HADOOP_BIN fs -rmr $OUTPUT

# paras for hadoop
MAP_CAP=1500
REDUCE_CAP=300
MAP_NUM_PER_NODE=5
REDUCE_NUM_PER_NODE=5
NUM_MAP=1200
NUM_REDUCE=100

echo ${OUTPUT}

${HADOOP_BIN} streaming \
    -D stream.num.map.output.key.fields=1 \
    -D num.key.fields.for.partition=1 \
    -D mapred.job.name="baidu_video" \
    -D mapred.job.map.capacity=$MAP_CAP \
    -D mapred.job.reduce.capacity=$REDUCE_CAP \
    -D mapred.map.capacity.per.tasktracker=$MAP_NUM_PER_NODE \
    -D mapred.reduce.capacity.per.tasktracker=$REDUCE_NUM_PER_NODE \
    -D mapred.map.tasks=$NUM_MAP \
    -D mapred.reduce.tasks=$NUM_REDUCE \
    -input  ${INPUT1}  \
    -output ${OUTPUT} \
    -mapper  "$python get_video_resource.py mapper"  \
    -reducer "$python get_video_resource.py reduce" \
    -file  "./get_video_resource.py"  \
    -cacheArchive $python_src \
    -partitioner "org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner" \
    -jobconf mapred.job.priority=$task_priority \
    
if [ $? -ne 0 ]; then
    echo "[FATAL]:hadoop failed!"
    exit 1
fi

${HADOOP_BIN} fs -cat ${OUTPUT}/* > temp
sort -t$'\t' -k2,2rg temp > $day_to_process.txt
rm temp
cp ../../conf/${video_dict_file} .
python merge.py ${video_dict_file} $day_to_process.txt ${video_line_to_merge}
rm $day_to_process.txt
cp ${video_dict_file} ../../conf/
