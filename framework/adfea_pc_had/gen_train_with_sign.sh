#!/bin/bash
# ToDo: get url_termlist pair from kr result

source ../conf/mine.conf

input0_path=$1/"part*A"
output_path=$2

HADOOP_BIN=$3
echo $HADOOP_BIN
if $HADOOP_BIN fs -test -e $output_path
then
    $HADOOP_BIN fs -rmr $output_path
fi

$HADOOP_BIN streaming \
    -input  $input0_path \
    -output $output_path \
    -mapper  "$python gen_train_with_sign.py" \
    -reducer "cat"  \
    -file "./gen_train_with_sign.py" \
    -file "./fea_sign_dict.txt"  \
    -cacheArchive "$python_src" \
    -jobconf mapred.job.name="get_list" \
    -jobconf mapred.job.map.capacity=1000 \
    -jobconf mapred.job.reduce.capacity=800 \
    -jobconf mapred.map.tasks=1200 \
    -jobconf mapred.reduce.tasks=100 \
    -jobconf mapred.job.priority=$task_priority \
    -jobconf stream.memory.limit=8000

if [ $? -ne 0 ]
     then
     echo "get_list error"
     exit 1
fi

echo "get_list success"

exit 0
