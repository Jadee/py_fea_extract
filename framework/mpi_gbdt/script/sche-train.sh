#!/bin/bash

set -x

CONF_PATH=conf_${TIME_STAMP}

source ${CONF_PATH}/train.conf
source script/functions.sh

mpirun mkdir -p log
mpirun mkdir -p output
mpirun mkdir -p output/model

#export RESTART_FOREST
#export RESTART_CONF

mpirun cp -r ${CONF_PATH}/ output
if [ $? -ne 0 ]; then
    echo "FATAL: cp conf/ to output failed"
    exit 1
fi

mpirun script/mpi-train-prepare.sh
if [ $? -ne 0 ]; then
    echo "FATAL: mpirun script/mpi-train-prepare.sh failed"
    exit 1
fi

gbdt_args="-c ${CONF_PATH}/gbdt-learner.conf -d data.txt -f \"output/model/${MODEL_FILE_NAME}\""
if [ ${IS_NEW_CONF_USED} -ne 0 ]; then
    gbdt_args="${gbdt_args} -i"
fi

if [ ${RESTART_FOREST} ]; then
    gbdt_args="${gbdt_args} --initialforest=initial-forest.data"
fi

if [ ${VALIDATION_DATA} ]; then
    gbdt_args="${gbdt_args} --validationdata=validation.data"
fi


mpirun bin/gbdt-learner ${gbdt_args}
if [ $? -ne 0 ]; then
    echo "FATAL: mpirun bin/gbdt-learner failed"
    exit 1
fi

