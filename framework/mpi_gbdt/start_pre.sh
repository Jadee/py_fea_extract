#!/bin/bash
# ToDo: get url_termlist pair from kr result

source ../conf/mine.conf 

declare current_path=`pwd`

function gbdt_bin()
{
    rm -rf gbdt_bin/*
    cp ../conf/gbdt_model gbdt_bin/
    cp $current_path/bin/gbdt-predictor gbdt_bin/
    cd $current_path/gbdt_bin
    $HADOOP_BIN fs -rmr $dependency_path"/gbdt_bin.tar.gz"
    tar -zcvf gbdt_bin.tar.gz *
    $HADOOP_BIN fs -put gbdt_bin.tar.gz $dependency_path
    if [[ $? -ne 0 ]]
    then
        echo "put gbdt model failed"
        exit 1
    fi
}

gbdt_bin
if [[ $? -ne 0 ]]    #½Å±¾Ö´ÐÐ²»³É¹¦
then
    echo "predict prepare failed"
    exit 1
fi

cd $current_path

input0_path=$fea_extract_path"/part*A"
output_path=$predict_output_path

if $HADOOP_BIN fs -test -e $output_path
then
    $HADOOP_BIN fs -rmr $output_path
fi

echo $fea_extract_path
echo $input0_path

$HADOOP_BIN streaming \
    -input  $input0_path \
    -output $output_path \
    -mapper  "$python predict.py mapper" \
    -reducer "$python predict.py reduce" \
    -file "./predict.py" \
    -file "./run.sh"  \
    -cacheArchive "$python_src" \
    -cacheArchive "$dependency_path/gbdt_bin.tar.gz#gbdt_bin" \
    -outputformat "org.apache.hadoop.mapred.lib.SuffixMultipleTextOutputFormat" \
    -jobconf mapred.job.name="mpi_predict" \
    -jobconf mapred.job.map.capacity=1500 \
    -jobconf mapred.job.reduce.capacity=800 \
    -jobconf mapred.map.tasks=6000 \
    -jobconf mapred.reduce.tasks=600 \
    -jobconf stream.memory.limit=4000 \
    -jobconf mapred.job.priority=$task_priority \

if [ $? -ne 0 ]
then
     echo "predict error"
     exit 1
fi

echo "predict success"

exit 0
