#!/bin/env python
# -*- coding: gbk -*-
import sys
import urllib
import ConfigParser

import Filter
import process_str

class parse_shitu_log():
    def __init__(self,fea_common_conf_filename):
        self.fea_common_conf_filename = fea_common_conf_filename
        self.pc_field_value = []
        self.wise_field_value = []
        self.parse_field_value = []
    
    def initialize(self):
        self.parse_common_conf()

    def parse_common_conf(self):
        '''@desc 将pc和wise，以及需要抽取的字段分别放到list中 '''
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open(self.fea_common_conf_filename, "r"))

        pc_shitu_field = self.config.get("pc_shitu_field", "af_map_schema") 
        pc_column = pc_shitu_field.strip().split(",")
        self.pc_field_value.append("key")      #key为searchid+cmatch+rank 为后续反查数据使用
        self.pc_field_value.append("source")   #pc or wise
        self.pc_field_value.append("p_value")  #预留的一个字段
        self.pc_field_value.append("label")    #label  默认为0
        for item in pc_column:
            self.pc_field_value.append(item.strip())

        wise_shitu_field = self.config.get("wise_shitu_field", "af_map_schema")
        wise_column = wise_shitu_field.strip().split(",")
        self.wise_field_value.append("key")      #key为searchid+cmatch+rank 为后续反查数据使用
        self.wise_field_value.append("source")   #pc or wise
        self.wise_field_value.append("p_value")  #预留的一个字段
        self.wise_field_value.append("label")    #label  默认为0
        for item in wise_column:
            self.wise_field_value.append(item.strip())

        after_parse_field = self.config.get("parse_log_field", "af_map_output_key")
        column=after_parse_field.strip().split(",")
        for item in column:
            self.parse_field_value.append(item)
    
    def parse_field(self, line, source):
        '''@desc 根据log 将字段用相应的值填充，返回需要抽取的字段值 '''
        data = line.strip('\n').split("\t")
        to_print = []
        field_value = []
        if source == "pc":
            field_value = self.pc_field_value
        elif source == "wise":
            field_value = self.wise_field_value

        mydict = {}
        length = len(field_value)
        for idx in xrange(0, length):
            try:
                temp = data[idx].replace("\n", " ")
                temp = temp.replace("\t", " ")
                mydict[field_value[idx]] = temp
            except:
                mydict[field_value[idx]] = "\N"

        if source == "pc":
            try:
                temp = mydict["non_per_click_q"]
                part = temp.split("%")
                mydict["non_per_click_q"] = part[1]
            except:
                mydict["non_per_click_q"] = mydict["per_click_q"]
        elif source == "wise":
            if mydict["non_per_click_q"] == "\N":
                mydict["non_per_click_q"] = mydict["per_click_q"]

        length = len(self.parse_field_value)
        for idx in xrange(0, length):
            to_print.append(mydict[self.parse_field_value[idx]])
        
        return "\t".join(to_print)

def read_white_list():
    '''@desc 读取(bidword\tshowurl)文件对log进行过滤 '''
    white_dict = {}
    input = open("white_list", "r")
    for line in input:
        if not line:
            continue
        data = line.strip().split("\t")
        white_dict[data[0]] = data[1]
        #white_dict[data[0]] = Filter.domain_url(data[1])
    return white_dict

def pretreatment(model_type, fea_common_conf_filename):
    '''@desc 对shitu log 进行预处理(抽取字段，过滤等） '''
    white_dict = read_white_list()
    parse_shitu_log_obj = parse_shitu_log(fea_common_conf_filename)
    parse_shitu_log_obj.initialize() 
    
    log_pc_show = 0
    log_pc_click = 0
    log_pc_price = 0
    log_wise_show = 0
    log_wise_click = 0
    log_wise_price = 0

    for line in sys.stdin:
        if not line:
            continue
        line = line.strip()
        data = line.split("\t")

        if line == "" or len(data) == 0:
            continue

        wise_cmatch = ["222", "223", "228", "229"]
        pc_cmatch = ["201", "204", "225"]

        if model_type == "predict":     # tag:predict 表示对shitu log 进行预估 
            bidword = urllib.unquote(data[23]).replace("\t", " ")   #解码
            bidword = process_str.handle_str(bidword).strip()
            if len(bidword) == 0:
                continue
            rec_field = []
            cmatch = data[9]
            wmatch = data[10]
            winfoid = data[11]
            key = data[6] + "," + data[9] + "," + data[12]  #searchid + cmatch + rank
            rec_field.append(winfoid)
            rec_field.append("record_field")
            rec_field.append(cmatch)
            rec_field.append(wmatch)
            rec_field.append(bidword)
            rec_field.append(data[0])    #show
            rec_field.append(data[1])    #click
            rec_field.append(data[2])    #price
            if cmatch in wise_cmatch:    #wise log
                showurl = urllib.unquote(data[50]).strip()
                log_wise_show += int(data[0])
                log_wise_click += int(data[1])
                log_wise_price += int(data[2])
                target_url = urllib.unquote(data[92]).strip();
                rec_field.append(target_url)
                print "\t".join(rec_field)
            elif cmatch in pc_cmatch:    #pc log
                showurl = urllib.unquote(data[51]).strip()
                log_pc_show += int(data[0])
                log_pc_click += int(data[1])
                log_pc_price += int(data[2])
                target_url = urllib.unquote(data[73]).strip();
                rec_field.append(target_url)
                print "\t".join(rec_field)
            else:
                rec_field.append("NULL")
                print "\t".join(rec_field)
                continue
        else:                           # 表示训练和测试过程, 训练和测试数据做了一些处理
            bidword = urllib.unquote(data[24]).replace("\t", " ")
            bidword = process_str.handle_str(bidword).strip()
            if len(bidword) == 0:
                continue
            cmatch = data[10]
            wmatch = data[11]
            winfoid = data[12]
            key = data[7] + "," + data[10] + "," + data[13]  #searchid + cmatch + rank
            rec_field = []
            rec_field.append(winfoid) 
            rec_field.append("record_field")
            rec_field.append(cmatch)
            rec_field.append(wmatch)
            rec_field.append(bidword)
            rec_field.append(data[1])    #show
            rec_field.append(data[2])    #click
            rec_field.append(data[3])    #price
            if cmatch in wise_cmatch:    #wise log
                showurl = urllib.unquote(data[51]).strip()
                target_url = urllib.unquote(data[93]).strip();
                rec_field.append(target_url)
                print "%s#C" %("\t".join(rec_field))
            elif cmatch in pc_cmatch:    #pc log
                showurl = urllib.unquote(data[52]).strip()
                target_url = urllib.unquote(data[74]).strip();
                rec_field.append(target_url)
                print "%s#C" %("\t".join(rec_field))
            else:
                rec_field.append("NULL")
                print "%s#C" %("\t".join(rec_field))
                continue
            
        
        # 一些白名单过滤，词表格式(bidword \t showurl)
        if model_type == "predict" and white_dict.has_key(bidword):
            part = white_dict[bidword].split(",")
            #proto, rest = urllib.splittype(showurl)
            #host, rest = urllib.splithost(rest)
            if showurl in part:
                continue
        
        '''
        # 只对精确匹配的广告进行预估
        if model_type == "predict" and wmatch != "63": 
            continue
        '''
        
        if cmatch in wise_cmatch:
            source = "wise"
        elif cmatch in pc_cmatch:
            source = "pc"
        else:
            continue
        p_value = 0
        label = 0

        # winfo + desc1 为key对log 进行去重
        if model_type == "predict":
            winfo = data[11]
            desc1 = data[25]
            nline = "%s\t%s\t%s\t%s\t%s" %(key, source, p_value, label, line)
            fea_value = parse_shitu_log_obj.parse_field(nline, source)
            if fea_value == "NULL" or fea_value == "":
                continue

            merge_key = winfo + "," + wmatch + "," + source + "\t" + desc1
            print "%s\t%s" %(merge_key, fea_value)
        else:
            winfo = data[12]
            nline = "%s\t%s\t%s\t%s" %(key, source, p_value, line)
            fea_value = parse_shitu_log_obj.parse_field(nline, source)
            if fea_value == "NULL" or fea_value == "":
                continue
            print "%s#A" %(fea_value)
    
    if model_type == "predict":
        print "tongji\tpc_log\t%s\t%s\t%s" %(log_pc_show, log_pc_click, log_pc_price)
        print "tongji\twise_log\t%s\t%s\t%s" %(log_wise_show, log_wise_click, log_wise_price)

def reduce(model_type, fea_common_conf_filename):
    '''@desc 在预估过程中对以winfo + wmatch 为key对log 进行去重 '''
    '''@desc 在去重过程中，对show，click等求和，对ctr， clickq等求均值 '''
    '''@desc 训练和测试过程不需要该过程 '''
    config = ConfigParser.ConfigParser()
    config.readfp(open(fea_common_conf_filename, "r"))
    
    # 读取mapper 输出的字段
    after_parse_field = config.get("parse_log_field", "af_map_output_key")
    column = after_parse_field.strip().split(",")
    field_list = []
    for item in column:
        field_list.append(item)

    # 读取需要做求和和求均值的字段
    avg_field = config.get("merge_field", "merge_value")
    avg_list = []
    column = avg_field.strip().split(",")
    for item in column:
        avg_list.append(item)

    last_key = ""

    sum_dict = {}
    cnt_dict = {}
    showdict = {}
    clickdict = {}
    pricedict = {}
    
    log_pc_show = 0
    log_pc_click = 0
    log_pc_price = 0
    log_wise_show = 0
    log_wise_click = 0
    log_wise_price = 0
    tongji_flag = False

    record_dict = {}

    for line in sys.stdin:
        if not line:
            continue
        line = line.strip()

        if line == "":
            continue

        data = line.split("\t")

        if data[1] == "record_field":
            print "%s#C" %(line)
            continue

        if model_type != "predict":
            length = len(data)
            to_print = []
            for idx in xrange(0, length):
                to_print.append(data[idx])
            outline = "\t".join(to_print)
            print "%s#A" %(outline)
            continue
        
        #tongji pc and wise data
        if data[0] == "tongji" and data[1] == "pc_log":
            log_pc_show += int(data[2])
            log_pc_click += int(data[3])
            log_pc_price += int(data[4])
            tongji_flag = True
            continue
        if data[0] == "tongji" and data[1] == "wise_log":
            log_wise_show += int(data[2])
            log_wise_click += int(data[3])
            log_wise_price += int(data[4])
            tongji_flag = True
            continue
        tongji_flag = False
        
        cur_key = data[0]   # key 是winfo + wmatch + source

        if last_key != cur_key and last_key != "":
            for record_key in record_dict:
                record = record_dict[record_key]
                
                # winfo + desc show,click,price 求和
                record["show"] = showdict[record_key]
                record["clk"] = clickdict[record_key]
                record["price"] = pricedict[record_key]
                
                for fld in sum_dict:            #求均值
                    record[fld] = float(sum_dict[fld]) / float(cnt_dict[fld])
                to_print = []
                for fld in field_list:
                    to_print.append(str(record[fld]))
                out_line = "\t".join(to_print)
                if len(out_line) != 0:
                    print "%s#A" %(out_line)
            sum_dict.clear()
            cnt_dict.clear()
            record_dict.clear()
            showdict.clear()
            clickdict.clear()
            pricedict.clear()

        last_key = cur_key
        mydict = {}
        out = {}
        length = len(data)
        for idx in xrange(2, length):
            mydict[field_list[idx - 2]] = data[idx]
            out[field_list[idx - 2]] = data[idx]

        rec_key = data[0] + "\t" + data[1]    #(winfo,wmatch \t desc1)
        record_dict[rec_key] = out
        try:
            showdict[rec_key] = showdict.get(rec_key, 0) + int(mydict["show"])
            clickdict[rec_key] = clickdict.get(rec_key, 0) + int(mydict["clk"])
            pricedict[rec_key] = pricedict.get(rec_key, 0) + int(mydict["price"])
        except:
            showdict[rec_key] = showdict.get(rec_key, 0) + 1
            clickdict[rec_key] = clickdict.get(rec_key, 0) + 0
            pricedict[rec_key] = pricedict.get(rec_key, 0) + 0

        for fld in avg_list:
            try:
                sum_dict[fld] = sum_dict.get(fld, 0) + int(mydict[fld])
                cnt_dict[fld] = cnt_dict.get(fld, 0) + 1
            except:
                sum_dict[fld] = sum_dict.get(fld, 0) + 0
                cnt_dict[fld] = cnt_dict.get(fld, 0) + 1

    if model_type == "predict" and tongji_flag == False:
        for record_key in record_dict:
            record = record_dict[record_key]
            
            record["show"] = showdict[record_key]
            record["clk"] = clickdict[record_key]
            record["price"] = pricedict[record_key]
            
            for fld in sum_dict:
                record[fld] = float(sum_dict[fld]) / float(cnt_dict[fld])
            to_print = []
            for fld in field_list:
                to_print.append(str(record[fld])) 
            out_line = "\t".join(to_print)
            if len(out_line) != 0:
                print "%s#A" %(out_line)

    if model_type == "predict" and log_pc_show != 0:
        print "pc_log\t%s\t%s\t%s#B" %(log_pc_show, log_pc_click, log_pc_price)
    if model_type == "predict" and log_wise_show != 0:
        print "wise_log\t%s\t%s\t%s#B" %(log_wise_show, log_wise_click, log_wise_price)

if __name__ == "__main__":
    if sys.argv[1] == "mapper":
        pretreatment(sys.argv[2], sys.argv[3])
    else:
        reduce(sys.argv[2], sys.argv[3])
