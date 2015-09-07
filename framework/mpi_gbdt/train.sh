#!/bin/bash

rm output/forest.data.138*
rm -rf gbdt-learner-temp

cat $1 | python train.py > temp_train
#awk -F "\t" '{print $1}' $1 > temp_train
bin/gbdt-learner -c conf/gbdt-learner.conf -d temp_train

rm gbdt_bin/forest.data
cp output/forest.data gbdt_bin/gbdt_model
cp bin/gbdt-predictor gbdt_bin/
mv output/forest.data ../conf/gbdt_model

rm -rf gbdt-learner-temp

cat $2 | python predict.py mapper > pre.txt

cat pre.txt | python auc.py
