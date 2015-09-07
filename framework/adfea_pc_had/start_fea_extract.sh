#!/bin/bash
# ToDo: get url_termlist pair from kr result

source ../conf/mine.conf

declare current_path=`pwd`
cp ../conf/af_parse.conf $current_path/adfea_py_conf/
cp ../conf/featurelist.conf $current_path/adfea_py_conf/

cp ../conf/fea_sign_dict.txt $current_path/adfea_py_conf/
fea_sign_file=$current_path/adfea_py_conf/fea_sign_dict.txt
if [ ! -f $fea_sign_file ]
then
    touch $current_path/adfea_py_conf/fea_sign_dict.txt
fi

function prepare()
{
    cd $current_path
    python compile.py   #对adfea_py_src下python脚本编译
    cd $current_path/adfea_py_src/
    rm adfea_py_src.tar.gz
    tar -zcvf adfea_py_src.tar.gz *
    if $HADOOP_BIN fs -test -e $dependency_path
    then
        echo "dependency ok"
    else
        $HADOOP_BIN fs -mkdir $dependency_path
    fi
    $HADOOP_BIN fs -rmr $dependency_path/adfea_py_src.tar.gz
    $HADOOP_BIN fs -put adfea_py_src.tar.gz $dependency_path

    cd $current_path/adfea_py_conf/
    rm adfea_py_conf.tar.gz
    tar -zcvf adfea_py_conf.tar.gz *
    if $HADOOP_BIN fs -test -e $dependency_path/adfea_py_conf.tar.gz
    then
        $HADOOP_BIN fs -rmr $dependency_path/adfea_py_conf.tar.gz
    fi
    $HADOOP_BIN fs -put adfea_py_conf.tar.gz $dependency_path
}

function extract_fea()
{
    cd $current_path
    model_type=`sed '/^type=/!d;s/.*=//' $current_path/adfea_py_conf/af_parse.conf`
    echo $model_type

    input0_path=$fea_field_path/"part-*"    #经过资源拼接和字段抽取的log
    output_path=$fea_extract_path           #特征抽取后的输出

    echo $fea_field_path

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
        NUM_MAP=6000
        NUM_REDUCE=0
    else
        NUM_MAP=500
        NUM_REDUCE=0
    fi

    $HADOOP_BIN streaming \
        -input  $input0_path \
        -output $output_path \
        -mapper  "$python fea_extract.py $model_type" \
        -file "./fea_extract.py" \
        -file "./compute_plsa_pzd.sh" \
        -cacheArchive "$python_src" \
        -cacheArchive "$dependency_path/adfea_py_conf.tar.gz#adfea_py_conf" \
        -cacheArchive "$dependency_path/adfea_py_src.tar.gz#adfea_py_src" \
        -cacheArchive "$plsa_sim_path#plsa" \
        -cacheArchive "$seg_word_dict_path#dict_seg_wordrank" \
        -outputformat "org.apache.hadoop.mapred.lib.SuffixMultipleTextOutputFormat" \
        -jobconf mapred.job.name="gen_fea_list" \
        -jobconf mapred.job.map.capacity=$MAP_CAP \
        -jobconf mapred.job.reduce.capacity=$REDUCE_CAP \
        -jobconf mapred.map.capacity.per.tasktracker=$MAP_NUM_PER_NODE \
        -jobconf mapred.reduce.capacity.per.tasktracker=$REDUCE_NUM_PER_NODE \
        -jobconf mapred.map.tasks=$NUM_MAP \
        -jobconf mapred.reduce.tasks=$NUM_REDUCE \
        -jobconf mapred.job.priority=$task_priority \
        -jobconf mapred.min.split.size=40000000 \
        -jobconf stream.memory.limit=8000
}

#####generat train fea_sign  #####
#训练阶段得到特征签名
function gen_train_fea_sign()
{
    cd $current_path
    $HADOOP_BIN fs -cat $fea_extract_path/part-*B > all_fea_sign
    awk -F "\t" '{print $1}' all_fea_sign | awk '!X[$0]++' | awk -F "\t" -v OFS="\t" '{print $1, NR}' > fea_sign_dict.txt

    cat $current_path/adfea_py_conf/featurelist.conf | python get_fea_id.py > fea_sign_dict.txt
    
    rm all_fea_sign
    cp fea_sign_dict.txt $current_path/adfea_py_conf/
    cp fea_sign_dict.txt ../conf/

    echo $fea_extract_path,$train_output_with_sign,$HADOOP_BIN

    sh gen_train_with_sign.sh $fea_extract_path $model_train_with_sign $HADOOP_BIN
    if [[ $? -ne 0 ]]    #脚本执行不成功
    then
        echo "gen_train_with_sign failed"
        exit 1
    fi
    python gen_gbdt_fea.py > gbdt_tmp.conf
    if [[ $? -ne 0 ]]    #脚本执行不成功
    then
        echo "gen gbdt fea failed"
        exit 1
    fi
    cat ../mpi_gbdt/conf/incomplete.conf gbdt_tmp.conf > ../mpi_gbdt/conf/gbdt-learner.conf
}

function main()
{
    prepare
    extract_fea
}

main
if [[ $? -ne 0 ]]    #脚本执行不成功
then
    echo "extract fea failed"
    exit 1
fi

model_type=`sed '/^type=/!d;s/.*=//' $current_path/adfea_py_conf/af_parse.conf`
if [ "$model_type" == "train" ]
then
    gen_train_fea_sign
fi

echo "get_list success"

exit 0
