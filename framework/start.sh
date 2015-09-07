#!/bin/bash
# ToDo: get url_termlist pair from kr result

declare current_path=`pwd`

if [ $# != 2 ]
then
    echo "please input model_type: train | test | predict"
    echo "please input status(join_prepare | join_resource | extract_feature | join_and_extract | predict | gen_badcase | all)"
    echo "    join_prepare: prepare landing page resource"
    echo "   join_resource: join ps abstract, lpq resource and so on to shitu log"
    echo "   join_word2vec: join feature word2vec "
    echo " extract_feature: extract feature from field value"
    echo "join and extract: include join_resource and extract_feature"
    echo "         predict: "
    echo "     gen_badcase: "
    echo "     pre_and_gen: " 
    echo "             all: include three processes"
    exit 1
fi

sh build.sh

function join_prepare()
{
    cd $current_path/join_resource
    sh start_join.sh 0 $1
    if [[ $? -ne 0 ]]    #脚本执行不成功 直接返回
    then
        echo "join_prepare failed"
        exit 1
    fi
}

function join_resource()
{
    #####  资源整合  #####
    cd $current_path/join_resource
    sh start_join.sh 1
    if [[ $? -ne 0 ]]    #脚本执行不成功 直接返回
    then
        echo "input_prepare failed"
        exit 1
    fi
    sh start_join.sh 2
    if [[ $? -ne 0 ]]    #脚本执行不成功 直接返回
    then
        echo "join_ps failed"
        exit 1
    fi
    sh start_join.sh 3
    if [[ $? -ne 0 ]]    #脚本执行不成功 直接返回
    then
        echo "join_word2vec failed"
        exit 1
    fi
}

function join_word2vec()
{
    cd $current_path/join_resource
    sh start_join.sh 3
    if [[ $? -ne 0 ]]    #脚本执行不成功 直接返回
    then
        echo "join_word2vec failed"
        exit 1
    fi
}

function extract_feature()
{
    cd $current_path/adfea_pc_had/
    sh start_fea_extract.sh
    if [[ $? -ne 0 ]]    #脚本执行不成功 直接返回
    then
        echo "join_lpq failed"
        exit 1
    fi
}

function predict()
{
    cd $current_path/mpi_gbdt
    sh start_pre.sh
    if [[ $? -ne 0 ]]    #脚本执行不成功 直接返回
    then
        echo "predict failed"
        exit 1
    fi
}

function gen_badcase()
{
    cd $current_path/gen_badcase
    sh start_run.sh
    if [[ $? -ne 0 ]]    #脚本执行不成功 直接返回
    then
        echo "gen_badcase failed"
        exit 1
    fi
}

function modify_conf()
{
    model_type=$1
    if [ $model_type == "train" ]
    then
        sed -i 's/type=test/type=train/g' $current_path/conf/af_parse.conf
        sed -i 's/type=predict/type=train/g' $current_path/conf/af_parse.conf

        sed -i 's/type=test/type=train/g' $current_path/conf/mine.conf
        sed -i 's/type=predict/type=train/g' $current_path/conf/mine.conf
    elif [ $model_type == "test" ]
    then
        sed -i 's/type=predict/type=test/g' $current_path/conf/af_parse.conf
        sed -i 's/type=train/type=test/g' $current_path/conf/af_parse.conf

        sed -i 's/type=predict/type=test/g' $current_path/conf/mine.conf
        sed -i 's/type=train/type=test/g' $current_path/conf/mine.conf
    elif [ $model_type == "predict" ]
    then
        sed -i 's/type=test/type=predict/g' $current_path/conf/af_parse.conf
        sed -i 's/type=train/type=predict/g' $current_path/conf/af_parse.conf

        sed -i 's/type=test/type=predict/g' $current_path/conf/mine.conf
        sed -i 's/type=train/type=predict/g' $current_path/conf/mine.conf
    else
        exit 1
    fi
}

modify_conf $1
if [[ $? -ne 0 ]]    #脚本执行不成功 直接返回
then
    echo "modify conf failed"
    exit 1
fi
#exit 0

if [ $2 == "all" ]
then
    join_resource
    extract_feature
    predict
    gen_badcase
fi

if [ $2 == "join_prepare" ]
then
    join_prepare $1
fi

if [ $2 == "join_resource" ]
then
    join_resource
fi

if [ $2 == "join_word2vec" ]
then
    join_word2vec
fi

if [ $2 == "extract_feature" ]
then
    extract_feature
fi

if [ $2 == "join_and_extract" ]
then
    join_resource
    extract_feature
fi

if [ $2 == "predict" ]
then
    predict
fi

if [ $2 == "gen_badcase" ]
then
    gen_badcase
fi

if [ $2 == "pre_and_gen" ]
then
    predict
    gen_badcase
fi


if [ $? -ne 0 ]
     then
     echo "gen badcase error"
     exit 1
fi
echo "gen badcase success"

exit 0
