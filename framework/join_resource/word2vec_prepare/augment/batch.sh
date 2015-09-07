#!/bin/bash

source ../../../conf/mine.conf
source ../../../conf/word2vec_task.conf

for i in `seq 90`;
    do
        t=`date --date="$i days ago" +%Y%m%d`
        echo $t
        $HADOOP_BIN dfs -test -e $url_augmented_by_query_path/${t}
        if [ $? -ne 0 ];then
            sh run.sh $t
            if [[ $? -ne 0 ]]    #½Å±¾Ö´ÐÐ²»³É¹¦ Ö±½Ó·µ»Ø
            then
                echo "gen url query failed"
                exit 1
            fi
        fi
        
    done

winfo_num=`$HADOOP_BIN fs -ls $url_augmented_by_query_path | wc -l`
echo $winfo_num

while [ $winfo_num -gt 92 ]
do
    file_name=`$HADOOP_BIN fs -ls $url_augmented_by_query_path | head -2 | tail -1 | awk -F " " '{print $NF}'`
    $HADOOP_BIN fs -rmr $file_name
    winfo_num=`$HADOOP_BIN fs -ls $url_augmented_by_query_path | wc -l`
done

if [[ $? -ne 0 ]]    #½Å±¾Ö´ÐÐ²»³É¹¦ Ö±½Ó·µ»Ø
then
    echo "exec failed"
    exit 1
fi

sh merge_everyDay_pairs.sh
if [[ $? -ne 0 ]]    #½Å±¾Ö´ÐÐ²»³É¹¦ Ö±½Ó·µ»Ø
then
    echo "merge_everyDay_pairs failed"
    exit 1
fi
