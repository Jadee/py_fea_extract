#!/bin/bash
# ToDo: get url_termlist pair from kr result


declare currend_path=`pwd`

function func_compute_word2vec()
{
    cd $currend_path/calc_word2vec_sim
    sh calc_embedding_score.sh
    if [[ $? -ne 0 ]]
    then
        echo "calc sim failed"
        exit 1
    fi
}

function func_join_other_fea()
{
    cd $currend_path
    source ../../conf/mine.conf

    MAP_CAP=1500
    REDUCE_CAP=1000
    MAP_NUM_PER_NODE=5
    REDUCE_NUM_PER_NODE=5
    if [ $type == "predict" ]
    then
        NUM_MAP=6000
        NUM_REDUCE=1500
    else
        NUM_MAP=800
        NUM_REDUCE=100
    fi
    
    input0_path=$daliy_task_word2vec_sim"/part*"
    input1_path=$fea_field_path"/part*"
    output_path=$my_hadoop_path"/badcase/model/fea_temp"
  
    $HADOOP_BIN fs -rmr $output_path
    echo $input1_path
    
    $HADOOP_BIN streaming \
    -D stream.num.map.output.key.fields=2 \
    -D num.key.fields.for.partition=1 \
    -input  $input0_path \
    -input  $input1_path \
    -output $output_path \
    -mapper  "$python join_other_fea.py mapper af_parse.conf"  \
    -reducer "$python join_other_fea.py reduce"  \
    -file "./join_other_fea.py"  \
    -file "../af_parse.conf"   \
    -cacheArchive $python_src \
    -partitioner "org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner" \
    -jobconf mapred.job.name="input_prepare" \
    -jobconf mapred.job.map.capacity=$MAP_CAP \
    -jobconf mapred.job.reduce.capacity=$REDUCE_CAP \
    -jobconf mapred.map.capacity.per.tasktracker=$MAP_NUM_PER_NODE \
    -jobconf mapred.reduce.capacity.per.tasktracker=$REDUCE_NUM_PER_NODE \
    -jobconf mapred.map.tasks=$NUM_MAP \
    -jobconf mapred.reduce.tasks=$NUM_REDUCE \
    -jobconf stream.memory.limit=2000 \
    -jobconf mapred.job.priority=$task_priority \

    if [[ $? -ne 0 ]]
    then
        echo "join word2vec failed"
        exit 1
    fi
    bak_fea_path=$my_hadoop_path"/badcase/model/bak_fea_field"
    $HADOOP_BIN fs -rmr $bak_fea_path
    $HADOOP_BIN fs -mv $fea_field_path $bak_fea_path
    $HADOOP_BIN fs -mv $output_path $fea_field_path
    if [[ $? -ne 0 ]]    #½Å±¾Ö´ÐÐ²»³É¹¦ Ö±½Ó·µ»Ø
    then
        echo "mv fea field failed"
        exit 1
    fi
}

#*************************** Run ***********************************************

func_compute_word2vec
if [[ $? -ne 0 ]]    #½Å±¾Ö´ÐÐ²»³É¹¦ Ö±½Ó·µ»Ø
then
    echo "compute_word2vec failed"
    exit 1
fi
func_join_other_fea
if [[ $? -ne 0 ]]    #½Å±¾Ö´ÐÐ²»³É¹¦ Ö±½Ó·µ»Ø
then
    echo "join word2vec sim failed"
    exit 1
fi

#*******************************************************************************

if [ $? -ne 0 ]
     then
     echo "get_list error"
     exit 1
fi
echo "get_list success"

exit 0
