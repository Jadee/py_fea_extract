#!/bin/bash
# ToDo: get url_termlist pair from kr result

declare current_path=`pwd`

source ../conf/mine.conf
cp ../conf/af_parse.conf  $current_path
cp ../conf/process_str.py $current_path

##### lpq 资源整合  #####
if [ $1 -eq 0 ]
then
    inputdate=`date "+%d"`
    if [[ $inputdate -eq 10 || $inputdate -eq 20 || $inputdate -eq 30 || $2 == "train" ]]
    then
        cd $current_path/extract_lp_fea
        cp ../process_str.py .
        sh extract_lp_fea.sh $HADOOP_BIN $lpq_feature_path $lpq_intent_path $wise_lpq_intent_path $lpq_join_out_path
        if [[ $? -ne 0 ]]    #脚本执行不成功 直接返回
        then
            echo "extract lpq_fea failed"
            exit 1
        fi
        cd $current_path/word2vec_prepare
        cp ../process_str.py .
        sh word2vec_prepare.sh
        if [[ $? -ne 0 ]]    #脚本执行不成功 直接返回
        then
            echo "word2vec prepare failed"
            exit 1
        fi
    fi
    cd $current_path/get_video_resource
    sh gen_video_resource.sh
    if [[ $? -ne 0 ]]    #脚本执行不成功 直接返回
    then
        echo "get video resource failed"
        exit 1
    fi
fi

##### 拼接 ps摘要等以bidword为key的资源
if [ $1 -eq 1 ]
then
    model_type=`sed '/^type=/!d;s/.*=//' $current_path/af_parse.conf`
    cd $current_path/input_prepare
    mid_out=$my_hadoop_path"/badcase/model/ba_temp"
    if [ $model_type == "predict" ]
    then
        while [[ 1 ]]     #判断pc log是否准备好
        do
            pc_log_num=`$HADOOP_BIN fs -ls $fcr_204_path | wc -l`
            echo "pc_204_num:",$pc_log_num
            [[ $pc_log_num -ge 20 ]] && break
            echo "waiting"
        done
        while [[ 1 ]]     #判断pc log是否准备好
        do
            pc_log_num=`$HADOOP_BIN fs -ls $fcr_201_path | wc -l`
            echo "pc_201_num:",$pc_log_num
            [[ $pc_log_num -ge 20 ]] && break
            echo "waiting"
        done
        while [[ 1 ]]     #判断pc log是否准备好
        do
            pc_log_num=`$HADOOP_BIN fs -ls $fcr_225_path | wc -l`
            echo "pc_225_num:",$pc_log_num
            [[ $pc_log_num -ge 20 ]] && break
            echo "waiting"
        done
        while [[ 1 ]]     #判断wise log是否准备好 
        do
            wise_log_num=`$HADOOP_BIN fs -ls $wise_path | wc -l`
            echo "wise_log_num:",$wise_log_num
            [[ $wise_log_num -ge 20 ]] && break
            echo "waiting"
        done
    fi
    sh start_pre.sh $HADOOP_BIN $mid_out $model_type $input_data_path
    if [[ $? -ne 0 ]]    #脚本执行不成功 直接返回
    then
        echo "input prepare failed"
        exit 1
    fi

    $HADOOP_BIN fs -cat $mid_out"/part*B" > $current_path/log_tongji_data
    if [[ $? -ne 0 ]]
    then
        echo "tongji log data failed"
        touch $current_path/log_tongji_data
    fi
    
    cd $current_path/join_ps
    cp ../process_str.py .
    sh start_gen_train.sh $mid_out $ps_term_path $bd_plsa_300_path $bd_trade_path $mid_output_path $HADOOP_BIN $user_trade_path $model_type
    if [[ $? -ne 0 ]]    #脚本执行不成功 直接返回
    then
        echo "join ps failed" 
        exit 1
    fi
fi

##### 拼接 lpq 资源 以url为key  #####
if [ $1 -eq 2 ]
then
    lpq_num=`$HADOOP_BIN fs -ls $lpq_join_out_path | wc -l`
    if [[ $? -ne 0 ]]
    then
        echo "lpq resource is not ready"
        exit 0
    fi
    if [ $lpq_num -lt 500 ]
    then
        echo "lpq resource is not ready"
        exit 0
    fi
    model_type=`sed '/^type=/!d;s/.*=//' $current_path/af_parse.conf`
    cd $current_path/join_lpq
    sh join_lpq_fea.sh $mid_output_path $lpq_join_out_path $fea_field_path $HADOOP_BIN $model_type
    if [[ $? -ne 0 ]]    #脚本执行不成功 直接返回
    then
        echo "join lpq failed"
        exit 1
    fi
fi

if [ $1 -eq 3 ]
then
    cd $current_path/join_other_fea
    cp ../process_str.py .
    sh join_other_fea.sh
    if [[ $? -ne 0 ]]    #脚本执行不成功 直接返回
    then
        echo "join word2vec sim failed"
        exit 1
    fi
fi

if [ $? -ne 0 ]
then
     echo "get_list error"
     exit 1
fi
echo "get_list success"

exit 0
