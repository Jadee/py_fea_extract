#!/bin/env python
# -*- coding:utf-8 -*-

import sys

'''@desc 产生GBDT模型训练的配置文件'''
def gen_gbdt_fea_def():
    dict = {}
    fea_type = ["FeatureNumerical", "FeatureNumericalPV", "FeatureNominal"]
    split_type = ["SplitNumBinary", "SplitNumPVBinary", "SplitNomBinary", "SplitNomMulti"]
    sign_file = open("fea_sign_dict.txt", "r")
    for line in sign_file:
        if not line:
            continue
        data = line.strip().split("\t")

        dict[data[0]] = data[1]

        print "[.@FEA]"
        print "SLOT : %s" %(data[1])
        print "NAME : %s" %(data[0])
        if data[0].find(",") >= 0:
            print "FEATURE_TYPE : %s" %(fea_type[2])
            print "SPLIT_TYPE : %s" %(split_type[2])
        else:
            print "FEATURE_TYPE : %s" %(fea_type[0])
            print "SPLIT_TYPE : %s" %(split_type[0])
        print
if __name__=="__main__":
    gen_gbdt_fea_def()
