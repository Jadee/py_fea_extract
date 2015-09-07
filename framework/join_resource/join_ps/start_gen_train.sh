#!/bin/bash
# ToDo: get url_termlist pair from kr result

source ../../conf/mine.conf

input0_path=$1"/part*A"   #log 输入
input1_path=$2            #ps 摘要
input2_path=$3            #bidword plsa 向量
input3_path=$4            #bidword  行业信息
output_path=$5            #输出路径

HADOOP_BIN=$6    #Hadoop 

user_trade_path=$7  #user 行业信息
model_type=$8       #类型  # train or test or predict

if $HADOOP_BIN fs -test -e $user_trade_path
then 
    rm db_new_user_trade.txt
    $HADOOP_BIN fs -get $user_trade_path db_new_user_trade.txt
fi

if $HADOOP_BIN fs -test -e $output_path
then
    $HADOOP_BIN fs -rmr $output_path
fi

echo "input: "$input0_path
echo "output: "$output_path

MAP_CAP=1500
REDUCE_CAP=800
MAP_NUM_PER_NODE=3
REDUCE_NUM_PER_NODE=3

if [ $model_type == "predict" ]
then
    NUM_MAP=6000
    NUM_REDUCE=1800
else
    NUM_MAP=600
    NUM_REDUCE=100
fi


$HADOOP_BIN streaming \
    -D stream.num.map.output.key.fields=2 \
    -D num.key.fields.for.partition=1 \
    -input  $input0_path \
    -input  $input1_path \
    -input  $input2_path \
    -input  $input3_path \
    -output $output_path \
    -mapper  "export PYTHONIOENCODING=GB18030 && export LANG=zh_CN.gb2312:en_US.UTF-8:zh_CN.UTF-8:en_US && $python join_shitu_ps.py mapper af_parse.conf" \
    -reducer "export PYTHONIOENCODING=GB18030 && export LANG=zh_CN.gb2312:en_US.UTF-8:zh_CN.UTF-8:en_US && $python join_shitu_ps.py reduce" \
    -file "./join_shitu_ps.py" \
    -file "./process_str.py"   \
    -file "../af_parse.conf"   \
    -file "./db_new_user_trade.txt" \
    -file "./compute_plsa_pzd.sh" \
    -file "./compute_word_trade.sh" \
    -file "./nqctool"  \
    -cacheArchive "$python_src" \
    -cacheArchive "$plsa_sim_path#plsa" \
    -cacheArchive "${calc_trade_path}/conf.tar.gz#conf" \
    -cacheArchive "${calc_trade_path}/data.tar.gz#data" \
    -partitioner "org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner" \
    -jobconf mapred.job.name="join_ps" \
    -jobconf mapred.job.map.capacity=$MAP_CAP \
    -jobconf mapred.job.reduce.capacity=$REDUCE_CAP \
    -jobconf mapred.map.capacity.per.tasktracker=$MAP_NUM_PER_NODE \
    -jobconf mapred.reduce.capacity.per.tasktracker=$REDUCE_NUM_PER_NODE \
    -jobconf mapred.map.tasks=$NUM_MAP \
    -jobconf mapred.reduce.tasks=$NUM_REDUCE \
    -jobconf stream.memory.limit=8000 \
    -jobconf mapred.job.priority=$task_priority \
    -jobconf mapred.min.split.size=100000000

#-cacheArchive "$plsa_sim_path#plsa" \
#-cacheArchive "${calc_trade_path}/conf.tar.gz#conf" \
#-cacheArchive "${calc_trade_path}/data.tar.gz#data" \
if [ $? -ne 0 ]
     then
     echo "get_list error"
     exit 1
fi
echo "get_list success"

exit 0
