#!/bin/env python
# -*- coding: utf-8 -*-
import sys
import urllib
import ConfigParser
import os

import process_str

class parse_shitu_log():
    join_key_index = 0
    userid_index = 0

    log_length = 0

    def __init__(self,fea_common_conf_filename):
        self.fea_common_conf_filename = fea_common_conf_filename
        self.parse_field_value = []

    def initialize(self):
        self.parse_common_conf()

    def parse_common_conf(self):
        # 读取输入文件的字段
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open(self.fea_common_conf_filename, "r"))

        after_parse_field = self.config.get("parse_log_field", "af_map_output_key")
        column = after_parse_field.strip().split(",")
        parse_shitu_log.log_length = len(column)
        for item in column:
            self.parse_field_value.append(item)

        join_key_literal = self.config.get("join_shitu_ps_key", "key")
        parse_shitu_log.join_key_index = self.parse_field_value.index(join_key_literal)
        parse_shitu_log.userid_index = self.parse_field_value.index("userid")

def read_user_trade():
    '''@desc 读取user的行业信息 '''
    user_trade = {}
    inputfile = open("db_new_user_trade.txt", "r")
    for line in inputfile:
        if not line:
            continue
        data = line.strip().split("\t")
        if len(data) < 4:
            continue
        if data[3] == "990101":
            continue
        user_trade[data[0]] = data[3]
    inputfile.close()
    return user_trade

def mapper(fea_common_conf_filename):
    '''@desc mapper阶段 对不同资源打上不同tag方便拼接 '''
    user_trade = read_user_trade()
    parse_shitu_log_obj = parse_shitu_log(fea_common_conf_filename)
    parse_shitu_log_obj.initialize()

    ps_dict = {}
    bd_trade = {}

    for line in sys.stdin:
        if not line:
            continue
        line = line.strip()
        data = line.split("\t")

        if len(line) == 0 or len(data) < 1:
            continue

        part = data[0].split(",")
        if len(part) == 3 and (data[1] == "pc" or data[1] == "wise"):    # log
            key = urllib.unquote(data[parse_shitu_log.join_key_index].strip()).replace("\t", " ")
            key = key.replace("\n", " ")
            key = process_str.handle_str(key)

            if len(key) == 0:
                continue

            userid = data[parse_shitu_log.userid_index]
            trade = user_trade.get(userid, 0)
            print "%s\t3\t%s\t%s" %(key, line, trade)   #打上tag 3

        elif len(data) == 3:   #bidword trade
            key = process_str.handle_str(data[1])
            if len(key) == 0:
                continue
            if bd_trade.has_key(key):
                continue
            bd_trade[key] = 1
            print "%s\t0\t%s" %(key, data[2])           #打上tag 0
        elif data[1] == "300":   #plsa_pzd 300
            try:
                key = process_str.handle_str(data[0])
            except:
                print >>sys.stderr, data[0]
                continue

            if len(key) == 0:
                continue
            value = "\N"
            if data[4] == "0":   #data[4] = 0 表示plsa向量为空
                print "%s\t1\t%s" %(key, value)
            else:
                idx = 5
                to_print = []
                length = len(data)
                while idx < length and (idx + 1) < length:
                    value = "%s:%s" %(data[idx], data[idx + 1])
                    to_print.append(value)
                    idx += 2
                print "%s\t1\t%s" %(key, ",".join(to_print))   #打上tag 1
        else:                     #ps term   
            key = process_str.handle_str(data[0])
            if len(key) == 0:
                continue
            if ps_dict.has_key(key):
                continue
            value = "\N"
            if int(data[2]) == 0:
                print "%s\t2\t%s" %(key, value)
            else:
                idx = 3
                to_print = []
                length = len(data)
                while idx < length and (idx + 1) < length:
                    value = "%s:%s" %(data[idx], data[idx + 1])
                    to_print.append(value)
                    idx += 2
                print "%s\t2\t%s" %(key, ",".join(to_print))    #打上tag 2
            ps_dict[key] = 1


def get_plsa_pzd(word):
    try:
        cmd = "sh compute_plsa_pzd.sh \"%s\"" %(word)
        ret = os.popen(cmd)
        while 1:
            line = ret.readline()
            if line == "":
                break
            plsa_pzd = line.strip('\n')

        part = plsa_pzd.split("\t")
        length = len(part)
        if length < 5 or part[4] == "0":
            return "\N"
        idx = 5
        printlist = []
        while idx < length:
            out = part[idx] + ":" + part[idx + 1]
            idx += 2
            printlist.append(out)
        return ",".join(printlist)
    except:
        return "\N"

def get_word_trade(word):
    try:
        cmd = "sh compute_word_trade.sh \"%s\"" %(word)
        ret = os.popen(cmd)
        while 1:
            line = ret.readline()
            if line == "":
                break
            value = line.strip("\n")
        data = value.split("\t")
        if len(data) < 2 or data[1] == "990101":
            return "\N"
        return data[1]
    except:
        return "\N"


def reduce():
    '''@desc mapper的输出会按照bidword + tag 进行排序 '''
    '''@desc reduce函数将不同资源拼接上log'''
    last_key = ""
    tag = 0
    ps_abs = "\N"     #ps 摘要 默认值为\N
    plsa_pzd = "\N"   #bidword plsa 向量 默认值为\N
    bd_trade = "\N"   #bidword 行业 默认值为\N

    for line in sys.stdin:
        if not line:
            continue
        data = line.strip().split("\t")
        cur_key = data[0]      # bidword
        tag = int(data[1])

        if tag == 0:
            plsa_pzd = "\N"
            ps_abs = "\N"
            bd_trade = data[2]
        elif tag == 1:
            if cur_key != last_key:
                bd_trade = "\N"
                ps_abs = "\N"
            plsa_pzd  = data[2]
        elif tag == 2:
            if cur_key != last_key:
                bd_trade = "\N"
                plsa_pzd = "\N"
            ps_abs = data[2]
        elif tag == 3:
            if cur_key != last_key:
                ps_abs = "\N"
                plsa_pzd = "\N"
                bd_trade = "\N"
            
            if plsa_pzd == "\N":
                plsa_pzd = get_plsa_pzd(cur_key)
            if bd_trade == "\N":
                bd_trade = get_word_trade(cur_key)
            
            to_print = []
            length = len(data)
            for idx in xrange(2, length):
                to_print.append(data[idx])
            to_print.append(bd_trade)
            to_print.append(plsa_pzd)
            to_print.append(ps_abs)
            print "\t".join(to_print)

        last_key = cur_key

if __name__ == "__main__":
    if sys.argv[1] == "mapper":
        mapper(sys.argv[2])
    elif sys.argv[1] == "reduce":
        reduce()

