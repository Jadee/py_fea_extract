#!/bin/bash

source ../../../conf/mine.conf
source ../../../conf/word2vec_task.conf

url_term_path=$url_augmented_merge_pairs_path"/part*"

echo $url_term_path
#**************************** Sub-module define ********************************
# Joint terms' and url vectors accoding to word_vector dict and url_vector dict 
function func_url_representation()
{
    $HADOOP_BIN fs -rmr $url_representation_express
    
    $HADOOP_BIN streaming \
    -D stream.num.map.output.key.fields=2 \
    -D num.key.fields.for.partition=1 \
    -inputformat "org.apache.hadoop.mapred.CombineTextInputFormat" \
    -input $term_embedding_path \
    -input $url_term_path \
    -output $url_representation_express \
    -mapper  "$python map_url_representation.py" \
    -reducer "$python red_url_representation.py" \
    -file "./map_url_representation.py" \
    -file "./red_url_representation.py" \
    -file "../process_str.py"  \
    -cacheArchive $seg_word \
    -cacheArchive $dict_seg_wordrank \
    -cacheArchive $python_src \
    -partitioner "org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner" \
    -jobconf mapred.job.name="joint-term-and-url-word2vec-vector" \
    -jobconf mapred.job.map.capacity=1500 \
    -jobconf mapred.job.reduce.capacity=1000 \
    -jobconf mapred.map.tasks=4000  \
    -jobconf mapred.job.priority=$task_priority \
    -jobconf mapred.reduce.tasks=1500
}
# Calculate query-url similarity score by word-url embedding
function func_calc_embedding_score()
{
    url_vec_output=$my_hadoop_path"/badcase/model/url_vec_tmp"
    
    $HADOOP_BIN fs -rmr $url_vec_output
        
    $HADOOP_BIN streaming \
    -input  $url_representation_express \
    -output $url_vec_output \
    -mapper  "$python map_calc_embedding_score.py" \
    -reducer "$python red_calc_embedding_score.py $vector_dimension" \
    -file "./map_calc_embedding_score.py" \
    -file "./red_calc_embedding_score.py" \
    -cacheArchive $python_src \
    -inputformat "org.apache.hadoop.mapred.CombineTextInputFormat" \
    -jobconf mapred.job.name="calc_word2vec_sim" \
    -jobconf mapred.job.map.capacity=1500  \
    -jobconf mapred.job.reduce.capacity=1000 \
    -jobconf mapred.map.tasks=1500  \
    -jobconf mapred.job.priority=$task_priority \
    -jobconf mapred.reduce.tasks=1500

    if [[ $? -ne 0 ]]    #½Å±¾Ö´ÐÐ²»³É¹¦ Ö±½Ó·µ»Ø
    then
        echo "gen url vec failed"
        exit 1
    fi
    $HADOOP_BIN fs -rmr $url_representation_vector
    $HADOOP_BIN fs -mv ${url_vec_output} $url_representation_vector
    if [[ $? -ne 0 ]]    #½Å±¾Ö´ÐÐ²»³É¹¦ Ö±½Ó·µ»Ø
    then
        echo "mv url vec failed"
        exit 1
    fi
}

#*******************************************************************************

#*************************** Run ***********************************************
func_url_representation
if [[ $? -ne 0 ]]    #½Å±¾Ö´ÐÐ²»³É¹¦ Ö±½Ó·µ»Ø
then
    echo "gen url query representation"
    exit 1
fi

func_calc_embedding_score
if [[ $? -ne 0 ]]    #½Å±¾Ö´ÐÐ²»³É¹¦ Ö±½Ó·µ»Ø
then
    echo "gen url vector"
    exit 1
fi

#*******************************************************************************

