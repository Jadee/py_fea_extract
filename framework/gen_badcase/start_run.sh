#!/bin/bash

source ../conf/mine.conf

#**********************generate badcase********************************************
function func_generate_badcase()
{
    sh gen_badcase.sh
    if [ $? -ne 0 ]; 
    then
        echo "gen badcase failed"
        exit 1
    fi

    rm -rf $today
    mkdir $today
    cp ../join_resource/log_tongji_data $today/
    $HADOOP_BIN fs -getmerge $gen_badcase_out $today/all_badcase
    if [ $? -ne 0 ];
    then
        echo "get badcase from hadoop failed"
        exit 1
    fi
}
#**********************************************************************************


#**********************filter rules************************************************
function func_filter_rules()
{
    filename=$today/all_badcase
    awk -F "," '{if($2 == 222 || $3 == 223) print $0}' $filename > $today/wise_shangfang

    touch $today/delta_winfoid
    awk -F "\t" -v OFS="\t" '{print $10, 7}' $filename | awk '!x[$0]++' >> $today/delta_winfoid
}
#**********************************************************************************

#**********************generate badcase********************************************
function func_statistic_influence()
{
    sh start_statistic_influence.sh
    if [ $? -ne 0 ];
    then
        echo "sta influence failed"
        exit 1
    fi

    rm $today/sta_influence
    $HADOOP_BIN fs -getmerge $sta_influence_out $today/sta_influence
    if [ $? -ne 0 ];
    then
        echo "get sta_influence from hadoop failed"
        exit 1
    fi
}
#**********************************************************************************


#**********************Subsequent_processing***********************************************
function func_Subsequent_processing()
{
    cmatch_out=$(python cmatch_tongji.py $today/sta_influence)

    eval $(awk -F "\t" 'BEGIN{pc_show = 0;pc_clk = 0;pc_price = 0;}{if($1 == 204 || $1 == 225){pc_show += $2;pc_clk += $3;pc_price += $4;}}END{print "pc_show="pc_show;print "pc_clk="pc_clk;print "pc_price="pc_price;}' $today/sta_influence)

    eval $(awk -F "\t" 'BEGIN{wise_show = 0;wise_clk = 0;wise_price = 0;}{if($1 == 222 || $1 == 223){wise_show += $2;wise_clk += $3;wise_price += $4;}}END{print "wise_show="wise_show;print "wise_clk="wise_clk;print "wise_price="wise_price;}' $today/sta_influence)


    unit=100
    pc_price_thre=`expr $pc_revenue_thre \* $unit`
    wise_price_thre=`expr $wise_revenue_thre \* $unit`

    echo $pc_price
    echo $pc_price_thre
    echo $wise_price
    echo $wise_price_thre
    echo $cmatch_out
    if [[ $pc_price -gt $pc_price_thre || $wise_price -gt $wise_price_thre ]]
    then
        echo "the effects of pc_zuoce_revenue or wise_shangfang_revenue is too large"
        echo "the effects of pc_zuoce_revenue: ", $pc_price
        echo "the pc_threshold is: ", $pc_price_thre
        echo "the effects of wise_zuoce_revenue: ", $wise_price
        echo "the wise_threshold is: ", $wise_price_thre
    else
        awk '!x[$0]++' $today/delta_winfoid >> ../online_dict/badcase_winfoid_list
    fi

    #qu chong
    awk '!x[$0]++' ../online_dict/badcase_winfoid_list > ../online_dict/dup
    mv ../online_dict/dup ../online_dict/badcase_winfoid_list
    md5sum ../online_dict/badcase_winfoid_list | awk -F " " '{print $1}' > ../online_dict/badcase_winfoid_list.md5

    winfo_num=`wc -l $today/delta_winfoid`
    python write_mail_content.py $pc_revenue_thre $wise_revenue_thre $winfo_num $today $cmatch_out > $today/mail_text_file.${today}
    if [[ $? -ne 0 ]] 
    then
        echo "write mail content failed"
        exit 1
    fi

    cat $today/all_badcase | python ran_case.py | awk '!x[$0]++' > $today/ran_eval_$today.txt
    if [[ $? -ne 0 ]]
    then
        echo "random case failed"
        exit 1
    fi

    sh send_mail.sh "${today}_badcase" $today/mail_text_file.${today} $today/ran_eval_$today.txt
    if [[ $? -ne 0 ]]
    then
        echo "send email failed"
        exit 1
    fi

    echo "success"
    exit 0
}
#****************************************************************************************


#********************clean work**********************************************************
function func_clean_work()
{
    current_path=`pwd`
    file_num=`ls -l $current_path | wc -l`

    echo $file_num
    while [[ $file_num -gt 90 ]]
    do
        file_name=`ls -l $current_path | head -2 | tail -1 | awk -F " " '{print $NF}'`
        echo $file_name
        rm -rf $file_name
        file_num=`ls -l $current_path | wc -l`
    done
}
#****************************************************************************************

#********************** run *************************************************************

func_generate_badcase
func_filter_rules
func_statistic_influence
func_Subsequent_processing
func_clean_work

#****************************************************************************************
