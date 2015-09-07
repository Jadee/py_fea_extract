#!/bin/bash

set -x

CONF_PATH=conf_${TIME_STAMP}

source ${CONF_PATH}/train.conf
source script/functions.sh

if [ ${RESTART_FOREST} ]; then
    ${HADOOP_HOME}/bin/hadoop fs -Dfs.default.name=${HADOOP_FS} -Dhadoop.job.ugi=${HADOOP_USER},${HADOOP_PASSWD} -get ${RESTART_FOREST} initial-forest.data
    if [ $? -ne 0 ]; then
        echo "FATAL: hadoop fs -get ${RESTART_FOREST} failed"
        exit 1
    fi
fi

if [ ${VALIDATION_DATA} ]; then
    ${HADOOP_HOME}/bin/hadoop fs -Dfs.default.name=${HADOOP_FS} -Dhadoop.job.ugi=${HADOOP_USER},${HADOOP_PASSWD} -get ${VALIDATION_DATA} validation.data
    if [ $? -ne 0 ]; then
        echo "FATAL: hadoop fs -get ${VALIDATION_DATA} failed"
        exit 1
    fi
fi

mkdir -p ${LOCAL_ROOT}
if [ $? -ne 0 ]; then
    echo "FATAL: mkdir failed"
    exit 1
fi

$HADOOP_HOME/bin/hadoop fs -Dfs.default.name=${HADOOP_FS} -Dhadoop.job.ugi=${HADOOP_USER},${HADOOP_PASSWD} -ls ${TRAIN_DATA_PATH} | grep "^-" | awk 'BEGIN{FS=" "}{print $NF}' > ${LOCAL_ROOT}/train_file_list.txt
if [ $? -ne 0 ]; then
    echo "FATAL: hadoop fs -ls failed"
    exit 1
fi

train_file_list=$(cat ${LOCAL_ROOT}/train_file_list.txt)
if [ $? -ne 0 ]; then
    echo "FATAL: cat ${LOCAL_ROOT}/train_file_list.txt failed"
    exit 1
fi

mkdir data
if [ $? -ne 0 ]; then
    echo "FATAL: mkdir data failed"
    exit 1
fi

set +x
i=0
>data.txt
for train_file in ${train_file_list}; do
    if (( i % ${OMPI_COMM_WORLD_SIZE} == ${OMPI_COMM_WORLD_RANK} )); then
        set -x
        if [ "X${DATA_PREPROC_CMD}" != "X" ]; then
        ${HADOOP_HOME}/bin/hadoop fs -Dfs.default.name=${HADOOP_FS} -Dhadoop.job.ugi=${HADOOP_USER},${HADOOP_PASSWD} -text ${train_file} | eval "${DATA_PREPROC_CMD}" > data/${i}.txt &
        else
        ${HADOOP_HOME}/bin/hadoop fs -Dfs.default.name=${HADOOP_FS} -Dhadoop.job.ugi=${HADOOP_USER},${HADOOP_PASSWD} -text ${train_file} > data/${i}.txt &
        fi
        set +x
    fi
    (( i++ ))
    if (( i % 1000 == 0 )); then
        wait
        if [ $? -ne 0 ]; then
            echo "FATAL: hadoop fs -text failed"
            exit 1
        fi
        cat /dev/null `find data/* -type f` >> data.txt
        if [ $? -ne 0 ]; then
            echo "FATAL: cat data/* > data.txt failed"
            exit 1
        fi
        rm -rf `find data/* -type f` 
        if [ $? -ne 0 ]; then
            echo "FATAL: rm -rf data/* failed"
            exit 1;
        fi
    fi
done
set -x

wait
if [ $? -ne 0 ]; then
    echo "FATAL: hadoop fs -text failed"
    exit 1
fi

cat /dev/null `find data/* -type f` >> data.txt
if [ $? -ne 0 ]; then
    echo "FATAL: cat data/* > data.txt failed"
    exit 1
fi
rm -rf `find data/* -type f` 
if [ $? -ne 0 ]; then
    echo "FATAL: rm -rf data/* failed"
    exit 1;
fi
