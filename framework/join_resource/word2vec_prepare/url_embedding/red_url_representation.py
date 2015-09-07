#! /usr/bin/env python

#*******************************************************************************
#brief: hadoop reducer script, joint term vector and url vector
#author: weichao05,lizhangfeng
#date:  2014-2-6
#input: term \t 1 \t vec
#       term \t 2 \t url \t freq
#output:
#       term \t vec \t url1 freq1 \t url2 freq2
#*******************************************************************************

import sys

toprint = "";

state = -1;


pre_key = "";
value = "";

for line in sys.stdin:
    flds = line.strip('\n').split("\t");
    flds_size = len(flds);
    if flds_size != 4 and flds_size != 3:
        continue;

    key = flds[0];
    tag = flds[1];

    if tag == "1":
        if toprint != "" and state > 0:
            print toprint;
            
        state = 0;
        value = flds[2];
        toprint = key + "\t" + flds[2];
        pre_key = key;
        
    elif tag == "2":
        
        freq = flds[3]
        
        if key != pre_key or flds[2][0:4] != "http" or len(flds[2]) <= 4:
            continue;
        else:
            toprint = toprint + "\t" + flds[2] + " " + freq;
            state = state + 1;
            if state == 50:
                print toprint;
                state = 0;
                toprint = pre_key + "\t" + value;

if toprint != "" and state > 0:
    print toprint;
