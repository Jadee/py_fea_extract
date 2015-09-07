#!/bash/bin

source conf/mine.conf

declare current_path=`pwd`


myfile=$current_path/online_dict/badcase_winfoid_list
if [ ! -f $myfile ]
then
    touch online_dict/badcase_winfoid_list
    md5sum $current_path/online_dict/badcase_winfoid_list | awk -F " " '{print $1}' > $current_path/online_dict/badcase_winfoid_list.md5
else
    md5sum $current_path/online_dict/badcase_winfoid_list | awk -F " " '{print $1}' > $current_path/online_dict/badcase_winfoid_list.md5
fi


mkdir tempfolder

myfile=$current_path/conf/video_dict.txt
if [ ! -f $myfile ]
then
    rm $current_path/tempfolder/video_dict.txt
    $HADOOP_BIN fs -get $wildword_conf/video_dict.txt $current_path/tempfolder/
    if [ $? -ne 0 ];
    then
        touch $current_path/tempfolder/video_dict.txt
    fi
    mv $current_path/tempfolder/video_dict.txt $current_path/conf/
else
    newfile=$data_pre_dir/video_dict.txt
    if [ ! -f $myfile ]
    then
        echo "continue"
    else
        cp $data_pre_dir/video_dict.txt $current_path/conf/
    fi
fi

myfile=$current_path/conf/famous_people_dict
if [ ! -f $myfile ]
then
    rm $current_path/tempfolder/famous_people_dict
    $HADOOP_BIN fs -get $wildword_conf/famous_people_dict $current_path/tempfolder/
    if [ $? -ne 0 ];
    then
        touch $current_path/tempfolder/famous_people_dict
    fi
    mv $current_path/tempfolder/famous_people_dict $current_path/conf/
fi
:<<block
    oldmd5sum=`md5sum $current_path/conf/famous_people_dict | awk -F " " '{print $1}'`
    $HADOOP_BIN fs -get $wildword_conf/famous_people_dict $current_path/tempfolder/
    newmd5sum=`md5sum $current_path/tempfolder/famous_people_dict | awk -F " " '{print $1}'`
    if [ "$oldmd5sum" != "$newmd5sum" ]
    then
        rm $current_path/conf/famous_people_dict
        mv $current_path/tempfolder/famous_people_dict $current_path/conf/
    fi
fi
block

myfile=$current_path/conf/sex_term_dict
if [ ! -f $myfile ]
then
    rm $current_path/tempfolder/sex_term_dict
    $HADOOP_BIN fs -get $wildword_conf/sex_term_dict $current_path/tempfolder/
    if [ $? -ne 0 ];
    then
        touch $current_path/tempfolder/sex_term_dict
    fi
    mv $current_path/tempfolder/sex_term_dict $current_path/conf/
fi

myfile=$current_path/conf/user_bidword_trade.dict
if [ ! -f $myfile ]
then
    rm $current_path/tempfolder/user_bidword_trade.dict
    $HADOOP_BIN fs -get $wildword_conf/user_bidword_trade.dict $current_path/tempfolder/
    if [ $? -ne 0 ];
    then
        touch $current_path/tempfolder/user_bidword_trade.dict
    fi
    mv $current_path/tempfolder/user_bidword_trade.dict $current_path/conf/
fi

myfile=$current_path/join_resource/input_prepare/Filter.so
if [ ! -f $myfile ]
then
    rm $current_path/tempfolder/Filter.so
    $HADOOP_BIN fs -get $wildword_conf/Filter.so $current_path/tempfolder/
    if [ $? -ne 0 ];
    then
        echo "miss Filter.so"
        exit 1
    fi
    mv $current_path/tempfolder/Filter.so $current_path/join_resource/input_prepare/
fi

myfile=$current_path/join_resource/extract_lp_fea/pc_wise_url_pair
if [ ! -f $myfile ]
then
    rm $current_path/tempfolder/pc_wise_url_pair
    $HADOOP_BIN fs -get $wildword_conf/pc_wise_url_pair $current_path/tempfolder/
    if [ $? -ne 0 ];
    then
        touch $current_path/tempfolder/pc_wise_url_pair
    fi
    mv $current_path/tempfolder/pc_wise_url_pair $current_path/join_resource/extract_lp_fea/
fi
:<<block
else
    rm $current_path/join_resource/extract_lp_fea/pc_wise_url_pair
    $HADOOP_BIN fs -get $wildword_conf/pc_wise_url_pair $current_path/tempfolder/
    if [ $? -ne 0 ];
    then
        touch $current_path/tempfolder/pc_wise_url_pair
    fi
    mv $current_path/tempfolder/pc_wise_url_pair $current_path/join_resource/extract_lp_fea/
fi
block

myfile=$current_path/adfea_pc_had/adfea_py_conf/trade_cos_pzd.txt
if [ ! -f $myfile ]
then
    rm $current_path/tempfolder/trade_cos_pzd.txt
    $HADOOP_BIN fs -get $wildword_conf/trade_cos_pzd.txt $current_path/tempfolder/
    if [ $? -ne 0 ];
    then
        touch $current_path/tempfolder/trade_cos_pzd.txt
    fi
    mv $current_path/tempfolder/trade_cos_pzd.txt $current_path/adfea_pc_had/adfea_py_conf/
fi

myfile=$current_path/adfea_pc_had/adfea_py_conf/trade_label_pzd
if [ ! -f $myfile ]
then
    rm $current_path/tempfolder/trade_label_pzd
    $HADOOP_BIN fs -get $wildword_conf/trade_label_pzd $current_path/tempfolder/
    if [ $? -ne 0 ];
    then
        touch $current_path/tempfolder/trade_label_pzd
    fi
    mv $current_path/tempfolder/trade_label_pzd $current_path/adfea_pc_had/adfea_py_conf/
fi

myfile=$current_path/join_resource/join_ps/nqctool
if [ ! -f $myfile ]
then
    rm $current_path/tempfolder/nqctool
    $HADOOP_BIN fs -get $wildword_conf/nqctool $current_path/tempfolder/
    if [ $? -ne 0 ];
    then
        echo "miss nqctool"
        exit 1
    fi
    mv $current_path/tempfolder/nqctool $current_path/join_resource/join_ps/
fi

myfile=$current_path/join_resource/join_ps/db_new_user_trade.txt
if [ ! -f $myfile ]
then
    rm $current_path/tempfolder/db_new_user_trade.txt
    $HADOOP_BIN fs -get $wildword_conf/db_new_user_trade.txt $current_path/tempfolder/
    if [ $? -ne 0 ];
    then
        touch $current_path/tempfolder/db_new_user_trade.txt
    fi
    mv $current_path/tempfolder/db_new_user_trade.txt $current_path/join_resource/join_ps/
fi

mypath=$current_path/adfea_pc_had/dict_seg_wordrank
if [ ! -d $mypath ]
then
    rm -rf $current_path/tempfolder/dict_seg_wordrank
    mkdir $current_path/tempfolder/dict_seg_wordrank
    $HADOOP_BIN fs -get $seg_word_dict_path $current_path/tempfolder/
    if [ $? -ne 0 ];
    then
        echo "miss dict_seg_wordrank"
        exit 1
    fi
    tar -zxvf $current_path/tempfolder/dict_seg_wordrank.tar.gz -C $current_path/tempfolder/dict_seg_wordrank/
    mv $current_path/tempfolder/dict_seg_wordrank $current_path/adfea_pc_had/
    rm -rf $current_path/tempfolder/*
fi

mypath=$current_path/adfea_pc_had/adfea_py_src/adfea_py_src/seg_word
if [ ! -d $mypath ]
then
    rm -rf $current_path/tempfolder/seg_word
    $HADOOP_BIN fs -get $wildword_conf/seg_word.tar.gz $current_path/tempfolder/
    if [ $? -ne 0 ];
    then
        echo "miss seg_word"
        exit 1
    fi
    tar -zxvf $current_path/tempfolder/seg_word.tar.gz -C $current_path/tempfolder/
    mv $current_path/tempfolder/seg_word $current_path/adfea_pc_had/adfea_py_src/adfea_py_src/
    rm -rf $current_path/tempfolder/*
fi

mypath=$current_path/mpi_gbdt/bin
if [ ! -d $mypath ]
then
    rm -rf $current_path/tempfolder/bin
    $HADOOP_BIN fs -get $wildword_conf/bin.tar.gz $current_path/tempfolder/
    if [ $? -ne 0 ];
    then
        echo "miss gbdt bin"
        exit 1
    fi
    tar -zxvf $current_path/tempfolder/bin.tar.gz -C $current_path/tempfolder/
    mv $current_path/tempfolder/bin $current_path/mpi_gbdt/
    cp $current_path/mpi_gbdt/bin/gbdt-predictor $current_path/mpi_gbdt/gbdt_bin/
    rm -rf $current_path/tempfolder/*
fi

mypath=$current_path/adfea_pc_had/plsa
if [ ! -d $mypath ]
then
    rm -rf $current_path/tempfolder/plsa
    mkdir $current_path/tempfolder/plsa
    $HADOOP_BIN fs -get $plsa_sim_path $current_path/tempfolder/
    if [ $? -ne 0 ];
    then
        echo "miss plsa"
        exit 1
    fi
    tar -zxvf $current_path/tempfolder/plsa.tar.gz -C $current_path/tempfolder/plsa/
    cp -r $current_path/tempfolder/plsa $current_path/adfea_pc_had/

    rm -rf $current_path/join_resource/join_ps/plsa
    cp -r $current_path/tempfolder/plsa $current_path/join_resource/join_ps/
    
    rm -rf $current_path/tempfolder/*
fi

mypath=$current_path/join_resource/join_ps/plsa
if [ ! -d $mypath ]
then
    cp -r $current_path/adfea_pc_had/plsa $current_path/join_resource/join_ps/
fi

mypath=$current_path/join_resource/join_ps/conf/
if [ ! -d $mypath ]
then
    rm -rf $current_path/tempfolder/*
    mkdir $current_path/tempfolder/conf
    $HADOOP_BIN fs -get $calc_trade_path/conf.tar.gz $current_path/tempfolder/
    if [ $? -ne 0 ];
    then
        echo "miss join_ps_conf"
        exit 1
    fi
    tar -zxvf $current_path/tempfolder/conf.tar.gz -C $current_path/tempfolder/conf
    mv $current_path/tempfolder/conf $current_path/join_resource/join_ps/
    rm -rf $current_path/tempfolder/*
fi

mypath=$current_path/join_resource/join_ps/data/
if [ ! -d $mypath ]
then
    rm -rf $current_path/tempfolder/*
    mkdir $current_path/tempfolder/data
    $HADOOP_BIN fs -get $calc_trade_path/data.tar.gz $current_path/tempfolder/
    if [ $? -ne 0 ];
    then
        echo "miss join_ps_data"
        exit 1
    fi
    tar -zxvf $current_path/tempfolder/data.tar.gz -C $current_path/tempfolder/data
    mv $current_path/tempfolder/data $current_path/join_resource/join_ps/
    rm -rf $current_path/tempfolder/*
fi

if [ $? -ne 0 ];
then
    echo "build failed"
    exit 1
fi

rm -rf $current_path/tempfolder
