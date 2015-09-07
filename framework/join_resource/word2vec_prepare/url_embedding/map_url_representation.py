#! /usr/bin/env python
# -*-coding:gbk-*-

#*******************************************************************************
#brief: hadoop mapper script, implement query segmentation and output data for
#       joint terms' and url vectors
#author: lichangcheng
#date:  2014-2-16
#*******************************************************************************

import sys
import urllib
import os
import math

import process_str

# For word segmentation
sys.path.append('seg_word')
from seg_word import wordrank_ecom

seg_path = './dict_seg_wordrank/worddict/'
tag_path = './dict_seg_wordrank/tagdict/'
ner_path = './dict_seg_wordrank/wordner.conf'
stop_words_path = "./dict_seg_wordrank/stop_words.txt"
seg_handle = wordrank_ecom.Seg_Rank();
seg_handle.seg_dict_init(seg_path, tag_path, ner_path, stop_words_path);

# input:
#   1. term \t tag(0) \t vector
#   2. target_url \t query \t click \t show \t ctr \t price
# output:
#   1. term \t tag(1) \t vector
#   2. term \t tag(2) \t target_url \t click
for line in sys.stdin:
    flds = line.strip().split("\t");
    flds_size = len(flds);
    if flds_size != 6 and flds_size != 3:
        continue;

    if flds_size == 3:  # word vector dict
        word = process_str.handle_str(flds[0]).strip()
        if len(word) == 0:
            continue
        
        length = 0;
        vec = flds[2].strip().split(' ');
        for ele in vec:
            length = length + float(ele) * float(ele);
        length = math.sqrt(length);
        vec = [str(float(x)/length) for x in vec];
        print "%s\t1\t%s" % (word, " ".join(vec));

    elif flds_size == 6:
        target_url = flds[0];
        if len(target_url.split("\t")) != 1 or target_url.isdigit():
            continue;
        bidword = process_str.handle_str(flds[1]).strip()

        freq = flds[2]
        if int(float(freq)) == 0:
            continue;
        
        if len(bidword.split("\t")) != 1 or len(bidword) > 100 or len(bidword) == 0:
            continue;
        try:
            (ret, token, netoken) = seg_handle.get_seg(bidword);
            if ret < 0:
                continue;
            for term, postag in token:
                term = term.strip()
                if len(term) == 0:
                    continue
                print "%s\t2\t%s\t%s" % (term, target_url, freq);
        except:
            continue;

