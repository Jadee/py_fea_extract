#!/bin/bash

set -x
source conf/train.conf
source script/functions.sh

HADOOP_FS=$(getHadoopConf "fs.default.name")
HDFS_USER_PASSWD=$(getHadoopConf "hadoop.job.ugi")

HADOOP_HOME=${LOCAL_HADOOP_HOME}
export HADOOP_HOME

TIME_STAMP=`date +%Y%m%d-%s`

CONF_PATH=conf_${TIME_STAMP}

cp -r conf ${CONF_PATH}
if [ $? -ne 0 ]; then
    echo "FATAL: cp conf failed."
    exit 1
fi

RETRY_NUM=0
SUCCESS_FLAG=1

HADOOP_CUR_PATH=${HDFS_ROOT}/${MPI_JOB_NAME}/${TIME_STAMP}
HADOOP_MODEL_LIST=${HADOOP_CUR_PATH}/*/output/rank-00000/model

while [ ${RETRY_NUM} -lt ${MAX_RETRY_NUM} ]; do

	if [ ${RETRY_NUM} -gt 0 ]; then
		echo "NOTICE: Retrying [${RETRY_NUM}/${MAX_RETRY_NUM}] ..."
	fi
	HADOOP_OUTPUT_DIR=${HADOOP_CUR_PATH}/${RETRY_NUM}

	${HADOOP_HOME}/bin/hadoop fs -ls ${HADOOP_MODEL_LIST}
	if [ $? -eq 0 ]; then
        RESTART_FOREST=`${HADOOP_HOME}/bin/hadoop fs -ls ${HADOOP_MODEL_LIST} | awk '{n=split($8,a,"/");print a[n-3],$8}' | sort -n -k1 | tail -n 1 | awk '{print $2}'`
	else
		RESTART_FOREST=${INITIAL_FOREST}
	fi

    qsub_f -N ${MPI_JOB_NAME} \
        --conf ${CONF_PATH}/qsub_f.conf \
        --hdfs ${HADOOP_FS} \
        --ugi ${HDFS_USER_PASSWD} \
        --hout ${HADOOP_OUTPUT_DIR} \
        --files bin,${CONF_PATH},script \
        -l nodes=${MPI_NODE_NUM},walltime=${WALL_TIME} script/sche-train.sh \
        -v RESTART_FOREST=${RESTART_FOREST},TIME_STAMP=${TIME_STAMP}

    SUCCESS_FLAG=$?
    if [ ${SUCCESS_FLAG} -eq 0 ]; then
        echo "MPI-TRAIN-SUCCESS: mpi-gbdt training success."
        ${HADOOP_HOME}/bin/hadoop fs -ls ${HADOOP_MODEL_LIST}
        if [ $? -eq 0 ]; then
            RESULT_FOREST=`${HADOOP_HOME}/bin/hadoop fs -ls ${HADOOP_MODEL_LIST} | awk '{n=split($8,a,"/");print a[n-3],$8}' | sort -n -k1 | tail -n 1 | awk '{print $2}'`
            if [ ${LOCAL_MODEL_PATH} ]; then
                echo "Downloading '${RESULT_FOREST}' to '${LOCAL_MODEL_PATH}' ..."
                ${HADOOP_HOME}/bin/hadoop fs -get ${RESULT_FOREST} ${LOCAL_MODEL_PATH}
                if [ $? -ne 0 ]; then
                    echo "FAILED: hadoop -get MODEL failed. [HADOOP_MODEL:${RESULT_FOREST}]"
                    exit 1
                fi
                echo "SUCCESS: [LOCAL_MODEL: '${LOCAL_MODEL_PATH}']"
            fi
            echo "SUCCESS: [HADOOP_MODEL:${RESULT_FOREST}]"
            exit 0
        else
            echo "FAILED: MPI-training succeed, but model file lost."
            exit 1
        fi
    else
        echo "NOTICE: Retry [${RETRY_NUM}/${MAX_RETRY_NUM}] failed."
    fi

    let RETRY_NUM++
done

echo "FATAL: mpi-gbdt training failed."
exit 1
