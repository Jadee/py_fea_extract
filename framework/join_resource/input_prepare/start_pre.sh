#!/bin/bash
# ToDo: get url_termlist pair from kr result

source ../../conf/mine.conf

HADOOP_BIN=$1   #hadoop 地址
shift
output_path=$1  #输出路径
shift
echo $output_path
model_type=$1
echo $model_type
shift

input0_path="$1"
shift
until [ $# -eq 0 ]
do
    input0_path=$input0_path" "$1     #多个输入路径合并（包含pc和wise的shitu log）
    shift
done

echo $input0_path

if $HADOOP_BIN fs -test -e $output_path
then
    $HADOOP_BIN fs -rmr $output_path
fi

MAP_CAP=1500
REDUCE_CAP=1000
MAP_NUM_PER_NODE=5
REDUCE_NUM_PER_NODE=5

if [ $model_type == "predict" ]
then
    NUM_MAP=5000
    NUM_REDUCE=1000
    SPLIT_SIZE=100000000
else
    NUM_MAP=800
    NUM_REDUCE=0
    SPLIT_SIZE=200000000
fi

$HADOOP_BIN streaming \
    -D stream.num.map.output.key.fields=2 \
    -D num.key.fields.for.partition=1 \
    -D mapred.combine.input.format.local.only=false \
    -input  $input0_path \
    -output $output_path \
    -mapper  "export PYTHONIOENCODING=GB18030 && export LANG=zh_CN.gb2312:en_US.UTF-8:zh_CN.UTF-8:en_US && $python prepare.py mapper $model_type af_parse.conf" \
    -reducer "export PYTHONIOENCODING=GB18030 && export LANG=zh_CN.gb2312:en_US.UTF-8:zh_CN.UTF-8:en_US && $python prepare.py reduce $model_type af_parse.conf" \
    -file "./prepare.py"  \
    -file "../af_parse.conf" \
    -file "./white_list"  \
    -file "./Filter.so"   \
    -file "../process_str.py"  \
    -cacheArchive $python_src \
    -partitioner "org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner" \
    -inputformat "org.apache.hadoop.mapred.CombineTextInputFormat"  \
    -outputformat "org.apache.hadoop.mapred.lib.SuffixMultipleTextOutputFormat" \
    -jobconf mapred.job.name="input_prepare" \
    -jobconf mapred.job.map.capacity=$MAP_CAP \
    -jobconf mapred.job.reduce.capacity=$REDUCE_CAP \
    -jobconf mapred.map.capacity.per.tasktracker=$MAP_NUM_PER_NODE \
    -jobconf mapred.reduce.capacity.per.tasktracker=$REDUCE_NUM_PER_NODE \
    -jobconf mapred.map.tasks=$NUM_MAP \
    -jobconf mapred.reduce.tasks=$NUM_REDUCE \
    -jobconf stream.memory.limit=2000 \
    -jobconf mapred.min.split.size=$SPLIT_SIZE \
    -jobconf mapred.job.priority=$task_priority \

if [ $? -ne 0 ]
     then
     echo "get_list error"
     exit 1
fi
echo "get_list success"

exit 0
