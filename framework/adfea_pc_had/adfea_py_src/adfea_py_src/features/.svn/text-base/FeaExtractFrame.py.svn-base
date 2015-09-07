#!/bin/env python
# -*- coding: gbk -*-
import sys
import ConfigParser
import urllib

from ExtractorClass import *

#定义特征抽取类的信息
class fea_info():
    def __init__(self):
        self.fea_name = ""                #特征名
        self.fea_slot = 0                 #槽位号
        self.fea_extractor_name = ""      #计算特征类名
        self.fea_extractor_object = ""    #计算特征对象
        self.fea_depend = []              #依赖项
        self.fea_argv = []                #参数
        self.fea_is_depend_other_fea = 0  #是否依赖计算出的特征
        self.fea_is_print = 0             #判断该特征是否抽取

#特征管理类
#完成特征列表文件解析
#特征的管理
class fea_extract_manage():

    def __init__(self, 
            fea_common_conf_filename, 
            fea_list_conf_filename, 
            fea_sign_filename = "", 
            fea_ins_sign_filename = ""):

        self.field_index_dict = {}       #保存输入数据中各字段的index
        self.fea_info_dict = {}          #保存特征数据 key：fea_name value: 特征信息
        self.add_token_field = []        #保存输出中需要保留的输入字段
        self.fea_sign_list = []          #特征抽取数据
        self.input_field_value = []      #保存输入数据字段

        self.extract_factory = fea_extract_factory()
        self.fea_common_conf_filename = fea_common_conf_filename
        self.fea_list_conf_filename = fea_list_conf_filename

        self.fea_sign_filename = fea_sign_filename
        if fea_sign_filename != "":
            self.file_fea_sign = open(self.fea_sign_filename, "w")

        self.fea_ins_sign_filename = fea_ins_sign_filename
        if fea_ins_sign_filename != "":
            self.file_fea_ins_sign = open(self.fea_ins_sign_filename, "w")

        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open("./adfea_py_conf/af_parse.conf", "rb"))
        self.model_type = self.config.get("model_type", "type")

    def __del__(self):
        if self.fea_sign_filename != "":
            self.file_fea_sign.close()
        if self.fea_ins_sign_filename != "":
            self.file_fea_ins_sign.close()
    
    # 解析文件schema,特征列表
    def initialize(self):
        self.parse_common_conf()
        self.parse_featurelist_conf()
        self.generate_extractor()

    def parse_featurelist_line(self, line, fea_info):
        '''@desc  读取特征文件 '''
        fea_info_dict = {}
        if line.strip()[0] == ".":
            fea_info.fea_is_print = 0
            line = line[1:]
        else:
            fea_info.fea_is_print = 1
        column = line.strip().split(";")
        for item in column:
            item_list = item.split("=")
            key = item_list[0]
            value = item_list[1]
            fea_info_dict[key] = str(value)
        fea_info.fea_name = fea_info_dict['name']
        fea_info.fea_slot = fea_info_dict['slot']
        fea_info.fea_extractor_name = fea_info_dict["class"]
        fea_info.fea_depend = fea_info_dict.get('depend').split(",")
        fea_info.fea_argv = fea_info_dict.get('argv').split(",")
        if fea_info.fea_extractor_name.find("combine") != -1:
            fea_info.fea_is_depend_other_fea = 1
        return 0

    def parse_common_conf(self):
        cf = ConfigParser.ConfigParser()
        cf.readfp(open(self.fea_common_conf_filename, "r"))
        schema_str = cf.get("joint_other_fea_field", "schema")
                
        column = schema_str.strip().split(",")
        i = 0
        for item in column:
            self.field_index_dict[item.strip()] = i
            i += 1

        add_token_str = cf.get("fea_out_add_token", "add_token")
        if add_token_str != "":
            self.add_token_field = add_token_str.split(",")
        else:
            return -1
        return 0

    def parse_featurelist_conf(self):
        path = self.fea_list_conf_filename
        f = open(path,"r")
        fea_infof_tmp = fea_info()
        while 1:
            fea_info_tmp = fea_info()
            line = f.readline()
            if not line:
                break
            line = line.strip().replace(" ", "")
            if len(line) == 0 or line[0] == "#":
                continue
            self.parse_featurelist_line(line, fea_info_tmp)
            self.fea_info_dict[fea_info_tmp.fea_name] = fea_info_tmp
        f.close()

    def generate_extractor(self):
        for i in self.fea_info_dict:
            self.extract_factory.regisotr_extractor(self.fea_info_dict[i])

    #  生成fea_str对应fea_sign的文件
    def generate_fea_str(self):
        for item in self.fea_info_dict:
            fea_info = self.fea_info_dict[item]
            s = "%s\t%s\n" %(fea_info.fea_extractor_object.fea_str, fea_info.fea_extractor_object.fea_sign)
            self.file_fea_sign.write(s)

    def generate_ins_str(self, line):
        column = line.strip('\n').split("\t")

        self.input_field_value = column
        for item in self.fea_info_dict:
            fea_info = self.fea_info_dict[item]
            if fea_info.fea_is_depend_other_fea == 1:    #对非依赖特征处理
                continue
            depend_field = fea_info.fea_depend
            #将特征依赖字段赋值
            depend_list = [ column[self.field_index_dict[fieldname] ] for fieldname in depend_field ]
            
            argv_list = fea_info.fea_argv   # 特征抽取时依赖的参数
            fea_info.fea_extractor_object.extract_sign(fea_info.fea_name, depend_list, argv_list, fea_info.fea_slot, self.model_type)

        for item in self.fea_info_dict:
            fea_info = self.fea_info_dict[item]
            if fea_info.fea_is_depend_other_fea == 0:
                continue
            depend_field = fea_info.fea_depend
            depend_list = [ self.fea_info_dict[fea_name].fea_extractor_object.fea_str  for fea_name in depend_field ]
            fea_info.fea_extractor_object.extract_sign(fea_info.fea_name, depend_list, argv_list, fea_info.fea_slot, self.model_type)

    def get_ins_feastr_list(self, line):
        column = line.strip().split("\t")
        self.input_field_value = column
        
        depend_id_list_all = []
        
        for item in self.fea_info_dict:
            #print item
            fea_info = self.fea_info_dict[item]
            depend_field = fea_info.fea_depend
            if fea_info.fea_is_depend_other_fea == 1:
                continue
            depend_list = [ column[self.field_index_dict[fieldname]] for fieldname in depend_field ]
            depend_id_list_all.extend([ self.field_index_dict[fieldname] for fieldname in depend_field ])
            argv_list = fea_info.fea_argv
            fea_info.fea_extractor_object.extract_fea_str(depend_list, argv_list, fea_info.fea_name, fea_info.fea_slot)

        for item in self.fea_info_dict:
            #print item
            fea_info = self.fea_info_dict[item]
            depend_field = fea_info.fea_depend
            if fea_info.fea_is_depend_other_fea == 0:
                continue
            depend_list = [self.fea_info_dict[fea_name].fea_extractor_object.fea_str for fea_name in depend_field ]
            argv_list = fea_info.fea_argv
            fea_info.fea_extractor_object.extract_fea_str(depend_list, argv_list, fea_info.fea_name, fea_info.fea_slot)

        return [ self.fea_info_dict[item].fea_extractor_object.fea_str for item in self.fea_info_dict],depend_id_list_all

    def generate_fea_id(self):
        tuple_tmp = () 
        line_id_list = []
        for item in self.fea_info_dict:
            fea_info = self.fea_info_dict[item]
            if fea_info.fea_is_print!=0:
                tuple_tmp = (fea_info.fea_extractor_object.fea_sign, fea_info.fea_extractor_object.fea_value)
                line_id_list.append(tuple_tmp)
        line_id_list.sort(cmp = lambda x, y:cmp(x[0], y[0]))
        
        self.fea_sign_list = ["%s:%s"%(i[0],i[1]) for i in line_id_list]

    def numeric_compare(self, fea1, fea2):
        part1 = fea1.split(":")
        part2 = fea2.split(":")
        return int(part1[0]) - int(part2[0])

    def print_ins_id(self):
        self.generate_fea_id()
        if self.model_type != "train":
            fea = " ".join(sorted(self.fea_sign_list, cmp = self.numeric_compare))
        else:
            fea = " ".join(self.fea_sign_list)

        label = self.input_field_value[self.field_index_dict["label"]]
        token = []
        token_str = ""
        if len(self.add_token_field) > 0:
            #token = [ self.input_field_value[self.field_index_dict[fieldname] ] for fieldname in self.add_token_field ]
            for fieldname in self.add_token_field:
                field_value = urllib.unquote(self.input_field_value[self.field_index_dict[fieldname]])
                field_value = field_value.replace("\n", "").strip()
                token.append(field_value)
            token_str = "\t".join(token)
            s = "%s\t%s" % (fea, token_str)
        else:
            s = fea
        weight = 1
        if self.fea_ins_sign_filename == "":
            ret_value = "%s %s %s" % (weight, label, s)
            return ret_value
            #print "%s %s %s#A" % (weight, label, s)
        else:
            self.file_fea_ins_sign.write(str(weight) + " " + label + " " + s + "\n")
            return None

    def print_feastr_id(self):
        feastr_id_dict = fea_extract_root().get_id_dict()
        for item in feastr_id_dict:
            if  self.fea_sign_filename == "":
                print "%s\t%s#B" % (item, feastr_id_dict[item])
            else:
                self.file_fea_sign.write(item + " " + str(feastr_id_dict[item]) + "\n")
            
# 生产出各个特征抽取类
class fea_extract_factory():
    def __init__(self):
        pass
    def __del__(self):
        pass
    def regisotr_extractor(self, fea_info):
        value = fea_info.fea_extractor_name
        fea_info.fea_extractor_object = eval(value + '()')   #对特征抽取函数进行类似注册功能

