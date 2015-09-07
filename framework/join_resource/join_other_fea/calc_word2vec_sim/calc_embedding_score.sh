#! /bin/bash

source ../../../conf/mine.conf
source ../../../conf/word2vec_task.conf

#***************************** HDFS common log path ****************************
model_type=$type

#*******************************************************************************


#**************************** Sub-module define ********************************

# unique input by winfoid
function func_unique_input()
{
    $HADOOP_BIN fs -rmr $daily_task_uniq_input 

    #unique_input_path=$input_data_path
    unique_input_path=$my_hadoop_path"/badcase/model/ba_temp/part*C"
        
    $HADOOP_BIN streaming \
    -D stream.num.map.output.key.fields=1 \
    -D num.key.fields.for.partition=1 \
    -D mapred.combine.input.format.local.only=false \
    -inputformat "org.apache.hadoop.mapred.CombineTextInputFormat"  \
    -input $unique_input_path \
    -output $daily_task_uniq_input \
    -mapper  "$python unique_input.py mapper $model_type" \
    -reducer "$python unique_input.py reduce" \
    -file "./unique_input.py" \
    -file "../process_str.py" \
    -cacheArchive $seg_word \
    -cacheArchive $dict_seg_wordrank \
    -cacheArchive $python_src \
    -partitioner "org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner" \
    -jobconf mapred.job.name="badcase_get_uniq_winfoid" \
    -jobconf mapred.job.map.capacity=1000  \
    -jobconf mapred.job.reduce.capacity=50 \
    -jobconf mapred.map.tasks=1000  \
    -jobconf mapred.job.priority=$task_priority \
    -jobconf mapred.reduce.tasks=50
}

# Joint terms' and url vectors accoding to word_vector dict and url_vector dict 
function func_joint_vector()
{
    $HADOOP_BIN fs -rmr $daliy_task_joint_vector
    
    $HADOOP_BIN streaming \
    -D stream.num.map.output.key.fields=2 \
    -D num.key.fields.for.partition=1 \
    -inputformat "org.apache.hadoop.mapred.TextInputFormat" \
    -input  $daily_task_uniq_input \
    -input  $term_embedding_path \
    -input  $url_representation_vector \
    -output $daliy_task_joint_vector \
    -mapper  "$python joint_vector.py mapper" \
    -reducer "$python joint_vector.py reduce" \
    -file "./joint_vector.py"  \
    -file "../process_str.py"  \
    -cacheArchive $seg_word \
    -cacheArchive $dict_seg_wordrank \
    -cacheArchive $python_src \
    -partitioner "org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner" \
    -jobconf mapred.job.name="badcase_joint_vector" \
    -jobconf mapred.job.map.capacity=1500     \
    -jobconf mapred.job.reduce.capacity=1000  \
    -jobconf mapred.map.tasks=5000  \
    -jobconf mapred.job.priority=$task_priority \
    -jobconf mapred.reduce.tasks=2000
}

# Calculate query-url similarity score by word-url embedding
function func_calc_embedding_score()
{
    $HADOOP_BIN fs -rmr $daliy_task_word2vec_sim
    
    $HADOOP_BIN streaming \
    -D stream.num.map.output.key.fields=1 \
    -D num.key.fields.for.partition=1 \
    -input  $daliy_task_joint_vector \
    -output $daliy_task_word2vec_sim \
    -mapper  "$python calc_embedding_score.py mapper"  \
    -reducer "$python calc_embedding_score.py reduce $vector_dimension" \
    -file "./calc_embedding_score.py" \
    -cacheArchive $python_src \
    -partitioner "org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner" \
    -jobconf mapred.job.name="badcase_get_word2vec_sim" \
    -jobconf mapred.job.map.capacity=1000  \
    -jobconf mapred.job.reduce.capacity=500 \
    -jobconf mapred.map.tasks=1000  \
    -jobconf mapred.job.priority=$task_priority \
    -jobconf mapred.reduce.tasks=500
}

#*******************************************************************************

#*************************** Run ***********************************************
url_vec_num=`$HADOOP_BIN fs -ls $url_representation_vector | wc -l`
if [[ $? -ne 0 ]]
then
    echo "url vector resource is not ready"
    exit 0
fi
if [ $url_vec_num -lt 500 ]
then
    echo "url vector resource is not ready"
    exit 0
fi

func_unique_input
if [[ $? -ne 0 ]]    #½Å±¾Ö´ÐÐ²»³É¹¦ Ö±½Ó·µ»Ø
then
    echo "gen unique input failed"
    exit 1
fi

func_joint_vector
if [[ $? -ne 0 ]]    #½Å±¾Ö´ÐÐ²»³É¹¦ Ö±½Ó·µ»Ø
then
    echo "joint vector failed"
    exit 1
fi

func_calc_embedding_score
if [[ $? -ne 0 ]]    #½Å±¾Ö´ÐÐ²»³É¹¦ Ö±½Ó·µ»Ø
then
    echo "calc sim failed"
    exit 1
fi
#*******************************************************************************

