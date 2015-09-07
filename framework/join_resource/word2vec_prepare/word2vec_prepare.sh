#!/bin/bash

source ../../conf/mine.conf
source ../../conf/word2vec_task.conf
current_path=`pwd`

# generate url-query pairs
# run it weekly
cd $current_path/augment
sh batch.sh
if [[ $? -ne 0 ]]    #½Å±¾Ö´ÐÐ²»³É¹¦ Ö±½Ó·µ»Ø
then
    echo "generate url-query pairs failed"
    exit 1
fi

# cal url-representation
# run it after new pairs generated
cd $current_path/url_embedding
sh comp_url_embedding.sh
if [[ $? -ne 0 ]]    #½Å±¾Ö´ÐÐ²»³É¹¦ Ö±½Ó·µ»Ø
then
    echo "gen url vector failed"
    exit 1
fi
