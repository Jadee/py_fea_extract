# -*- coding: gb18030 -*-
# Written by Wei Chao, lizhangfeng 2013/10/14
# This program is used as a mapper to extract landing page feautres;
# It is the same as json_decode_mapper.py but more flexable
# Users can change paras in conf.py, specify fields and corresponding
# process functions decoding them.
# 
# Requirement : conf.py
# 

import sys
import json
import getopt
import ConfigParser
import urllib

import conf
import process_str
# default process for a feature
# if this feature (decoded from a json string) is not a string,
# transfer it.
def default_parser(strings):
    if strings == "":
        return "\N"
    else:
        return str(strings);
    
# main
def mapper(conf_file_name, separator='\t'):
    reload(sys);
    sys.setdefaultencoding("GB18030")

    config = ConfigParser.ConfigParser()
    config.readfp(open(conf_file_name, "r"))
    lpq_items = config.items("lpq_fea_resource")
    fea_list = []
    for item in lpq_items:
        fea_list.append(item[1])

    fea_dict = {}
    intent_dict = {}

    for line in sys.stdin:
        if not line:
            break;
        
        line = line.strip('\n');
        data = line.split("\t");

        if (len(data) == 3):
            # input is landing page feature
            if line == "":
                continue;
            
            url = data[0]
            if fea_dict.has_key(url):
                continue
            fea_dict[url] = 0

            json_data = data[2];
            try:
                decoded = json.loads(json_data, encoding='GB18030');
            except Exception, e:
                continue;

            to_print = [];
            fail = 0;        
            for fea in fea_list:
                if not decoded.has_key(fea):
                    fail = 1;
                    break;
                else:
                    if not conf.fea_parser_dict.has_key(fea):
                        parser_name = default_parser;
                    else:
                        parser_name = conf.fea_parser_dict[fea];
                ret = parser_name(decoded[fea]);
                if(ret == None):
                    fail = 1;
                    break;
                else:
                    if ret != "\N":
                        ret = process_str.handle_str(ret)
                    if len(ret) == 0:
                        to_print.append("\N");
                    else:
                        to_print.append(ret);

            if fail == 1:
                continue;
            else:
                flag = 0
                for elem in to_print:
                    if elem != "\N":
                        flag = 1
                        break
                if flag == 0:
                    continue
                lpq_fea = "\t".join(to_print)
                lpq_fea = lpq_fea.strip()
                if len(lpq_fea) == 0:
                    continue
                print "%s\t0\t%s" %(url, lpq_fea)
        else:     #lpq intent fea
            if len(data) != 5:
                continue
            url = data[0]
            if intent_dict.has_key(url):
                continue
            intent_dict[url] = 1

            to_print = []
            if len(data[3].strip()) == 0:
                to_print.append("\N")
            else:
                tmp = data[3].replace(",", "")
                to_print.append(tmp.replace(";", ","))

            temp_list = []
            lpq_intent = data[4].split("|")
            if len(lpq_intent) == 3:
                part = lpq_intent[0].split(";")
                if len(part) >= 2:
                    cnt = int(part[1])
                    if cnt != 0:
                        length = len(part)
                        for idx in xrange(2, length):
                            tmp = part[idx].split(":")
                            pro = float(tmp[1]) / 100000
                            if pro > 0.0001:
                                value = "%s:%s" %(tmp[0], pro)
                                temp_list.append(value)

            if len(temp_list) == 0:
                to_print.append("\N")
            else:
                to_print.append(",".join(temp_list))
            flag = 0
            for elem in to_print:
                if elem != "\N":
                    flag = 1
                    break
            if flag == 1:
                print "%s\t1\t%s" %(url, "\t".join(to_print))

def read_pc_wise_url_match():
    match_dict = {}
    inputfile = open("pc_wise_url_pair", "r")
    for line in inputfile:
        if not line:
            continue
        data = line.strip().split("\t")
        match_dict[data[0]] = data[1]
    inputfile.close()
    return match_dict
                
def reduce(separator='\t'):
    last_key = ""
    match_dict = read_pc_wise_url_match()
    for line in sys.stdin:
        if not line:
            break
        line = line.strip('\n');
        if line == "":
            continue

        data = line.split("\t");
        if len(data) <= 2:
            continue
        cur_key = data[0] + "\t" + data[1]
        if cur_key == last_key:
            continue

        last_key = cur_key;
        to_print =  []
        length = len(data)
        for idx in xrange(2, length):
            to_print.append(data[idx])
        
        if data[1] == "0":
            output = "\t".join(to_print)
            if len(output) == 0:
                continue
            print "%s\t%s#A" %(cur_key, output)
            if match_dict.has_key(data[0]):
                print "%s\t0\t%s#A" %(match_dict[data[0]], output)
        elif data[1] == "1":
            output = "\t".join(to_print)
            if len(output) == 0:
                continue
            print "%s\t%s#B" %(cur_key, output)
            if match_dict.has_key(data[0]):
                print "%s\t1\t%s#B" %(match_dict[data[0]], output)

if __name__ == "__main__":
    if sys.argv[1] == "mapper":
        reload(sys);
        sys.setdefaultencoding("GB18030")
        mapper(sys.argv[2])
    elif sys.argv[1] == "reduce":
        reduce()
    else:
        sys.exit(0)
       
