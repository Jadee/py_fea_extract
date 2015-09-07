#!/bin/env python
# -*- coding: gbk -*-

#######################################################################
#
# @Brief:    Extract feature frame
# @Author:   Guo Wentao,guoshuai,lizhangfeng
# @Email:    guowentao@baidu.com,guoshuai02@baidu.com,
# @Date:     2012-12-17
#
#######################################################################

import sys
import ConfigParser
from hashlib import md5
from MyExtractorClass import *

# 特征抽取类的父类，所有特征抽取类都需要继承
class fea_extract_root():
    '''general fe_extract root '''
    id = 0
    id_dict = {}
    stat_pos_dict = {}
    stat_show_dict = {}
    fea_sign_dict = {}
    
    def __init__(self):
        self.fea_sign = ""   #特征签名
        self.fea_value = ""  #特征值
        self.fea_str = ""    #字面

    def load_fea_sign(self):
        config = ConfigParser.ConfigParser()
        config.readfp(open("./adfea_py_conf/adfea_py.conf", "rb"))
        fea_sign_dict_path = config.get("fea_sign_dict", "path") 
        fea_sign_dict_file = open(fea_sign_dict_path, "r")
        for line in fea_sign_dict_file:
            if not line:
                break
            data = line.strip().split("\t")
            if len(data) < 2:
                continue
            fea_extract_root.fea_sign_dict[data[0]] = data[1]

    def get_id_dict(self):
        return self.__class__.id_dict
    def get_stat_pos_dict(self):
        return self.__class__.stat_pos_dict
    def get_stat_show_dict(self):
        return self.__class__.stat_show_dict
    def make_sign():
        pass

    def get_fea_id(self, fea_str, model_type):
        if model_type != "train":
            if fea_extract_root.fea_sign_dict.has_key(fea_str):
                return fea_extract_root.fea_sign_dict[fea_str]
            else:
                return len(fea_extract_root.fea_sign_dict) + 1
        else:
            if(fea_str in fea_extract_root.id_dict):
                #return fea_extract_root.id_dict[str]
                return fea_str
            else:
                fea_extract_root.id += 1
                fea_extract_root.id_dict[fea_str] = fea_extract_root.id
                #return fea_extract_root.id 
                return fea_str

    def get_fea_another_id(self,str):
        if(str in self.__class__.id_dict):
            return self.__class__.id_dict[str]
        else:
            self.__class__.id +=1
            self.__class__.id_dict[str]=self.__class__.id
            return self.__class__.id 

    def sign_str(self,str):
        m = md5()
        m.update(str)
        return m.hexdigest()
    def extract_sign(self, fea_name, dependlist, argvlist, slot, model_type):
        pass

base_obj = fea_extract_root()
base_obj.load_fea_sign()

class fea_discrete(fea_extract_root):
    '''@desc 离散类特征处理'''
    def extract_sign(self, fea_name, dependlist, argvlist, slot, model_type):
        self.temp = "-".join(dependlist)
        self.fea_str = "%s,%s" %(fea_name, fea_temp)
        self.fea_value = 1
        self.fea_sign = fea_extract_root.get_fea_id(self, self.fea_str, model_type)
    
    def extract_fea_str(self, dependlist, argvlist, fea_name, slot):
        self.fea_str = "%s,%s" %(fea_name, "-".join(dependlist))
        self.fea_value = 1

    def get_id_dict(self):
        return fea_extract_root.get_id_dict(self)


class fea_continues(fea_extract_root):
    '''continues feature 
       notice:linear ralatoin
    '''
    def __init__(self):
        self.seg_rank = Extractor_seg_word()

    def __del__(self):
        pass

    def extract_sign(self, fea_name, dependlist, argvlist, slot, model_type):
        self.fea_str = "%s" %(fea_name)
        self.get_fea_value(dependlist, argvlist)
        self.fea_sign = fea_extract_root.get_fea_id(self, self.fea_str, model_type)

    def extract_fea_str(self, dependlist, argvlist, fea_name, slot):
        self.fea_str = "%s" %(fea_name)
        self.get_fea_value(dependlist, argvlist)

    def get_id_dict(self):
        return fea_extract_root.get_id_dict(self)

    def get_fea_value(self, dependlist, argvlist):
        self.fea_value = "-".join(dependlist)
    pass

### MyExtractor
class fea_cont_s_direct(fea_continues):
    def get_fea_value(self, dependlist, argvlist):
        try:
            if len(dependlist) == 1:
                self.fea_value = float(dependlist[0]) / float(argvlist[0])
            else:
                self.fea_value = "-".join(dependlist)
        except:
            self.fea_value = -1

class fea_cont_s_product(fea_continues):
    def get_fea_value(self, dependlist, argvlist):
        try:
            length = len(dependlist)
            ans = 1
            for idx in xrange(0, length):
                ans = ans * float(dependlist[idx]) / float(argvlist[0])
            self.fea_value = float(ans)
        except:
            self.fea_value = -1

class fea_cont_s_bdtype(fea_continues):
    def get_fea_value(self, dependlist, argvlist):
        if len(dependlist) == 1:
            try:
                if len(unicode(dependlist[0],'gb2312')) == len(dependlist[0]):
                    self.fea_value = 1
                else:
                    self.fea_value = 0
            except:
                self.fea_value = -1
        else:
            self.fea_value = -1

class fea_cont_s_term_num(fea_continues):
    def get_fea_value(self, dependlist, argvlist):
        self.fea_value = str(self.seg_rank.s_term_num(dependlist))

class fea_cont_s_matched_term_num(fea_continues):
    def get_fea_value(self, dependlist, argvlist):
        self.fea_value = str(self.seg_rank.s_match_term_num(dependlist, argvlist))

class fea_cont_s_uniq_matched_term_num(fea_continues):
    def get_fea_value(self, dependlist, argvlist):
        self.fea_value = str(self.seg_rank.s_uniq_match_term_num(dependlist, argvlist)) 

class fea_cont_s_matched_term_length(fea_continues):
    def get_fea_value(self, dependlist, argvlist):
        self.fea_value = str(self.seg_rank.s_match_term_length(dependlist, argvlist))

class fea_cont_s_uniq_matched_term_length(fea_continues):
    def get_fea_value(self, dependlist, argvlist):
        self.fea_value = str(self.seg_rank.s_uniq_match_term_length(dependlist, argvlist))
    
class fea_cont_s_longest_common_string(fea_continues):
    def get_fea_value(self, dependlist, argvlist):
        self.fea_value = str(self.seg_rank.s_longest_common_string(dependlist, argvlist))

class fea_cont_s_longest_common_string_uncontinue(fea_continues):
    def get_fea_value(self, dependlist, argvlist):
        self.fea_value = str(self.seg_rank.s_longest_common_string_uncontinue(dependlist, argvlist))

class fea_cont_s_edit_distance(fea_continues):
    def get_fea_value(self, dependlist, argvlist): 
        self.fea_value = str(self.seg_rank.s_edit_distance(dependlist))

class fea_cont_s_similarity(fea_continues):
    def get_fea_value(self, dependlist, argvlist):
        self.fea_value = str(self.seg_rank.s_similarity(dependlist))

class fea_cont_s_cos_dict(fea_continues):
    def get_fea_value(self, dependlist, argvlist):
        self.fea_value = str(self.seg_rank.s_cos_dict(dependlist, argvlist))

class fea_cont_s_plsa_sim(fea_continues):
    def get_fea_value(self, dependlist, argvlist):
        self.fea_value = str(self.seg_rank.s_plsa_sim(dependlist))

class fea_cont_s_match_industry(fea_continues):
    def get_fea_value(self, dependlist, argvlist):
        self.fea_value = str(self.seg_rank.s_match_industry(dependlist, argvlist))

class fea_cont_s_trade_cos_sim(fea_continues):
    def get_fea_value(self, dependlist, argvlist):
        self.fea_value = str(self.seg_rank.s_trade_cos_sim(dependlist, argvlist))

class fea_cont_s_latent_relevance_sim(fea_continues):
    def get_fea_value(self, dependlist, argvlist):
        self.fea_value = str(self.seg_rank.s_latent_relevance_sim(dependlist, argvlist))
    
####


class fea_per_bucket(fea_extract_root):
    def extract_sign(self, fea_name, dependlist, argvlist,slot, model_type):
        if len(dependlist) != 1:
            print >> sys.stderr, 'mul_score arg not equal 1'
            sys.exit()
        f_score = float(dependlist[0])
        scale = int(argvlist[0])
        score = int(f_score * scale)
        self.fea_str = "%s,%s" %(fea_name, score)
        self.fea_sign = fea_extract_root.get_fea_id(self, self.fea_str, model_type)
        self.fea_value = 1

    def extract_fea_str(self, dependlist, argvlist, fea_name, slot):
        if len(dependlist) != 1:
            print >> sys.stderr, 'mul_score arg not equal 1'
            sys.exit()
        f_score = float(dependlist[0])
        scale = int(argvlist[0])
        score = int(f_score * scale)
        self.fea_str = "%s,%s" %(fea_name, score)
        self.fea_value = 1

    def get_id_dict(self):
        return fea_extract_root.get_id_dict(self)

class fea_combine(fea_extract_root):

    def extract_sign(self, fea_name, dependlist, argvlist, slot, model_type):
        if len(dependlist) == 0:
            print >> sys.stderr, 'len(dependlist) == 0'
            sys.exit()
        self.fea_str = "%s,%s" %(fea_name,"-".join(dependlist))
        self.fea_sign = fea_extract_root.get_fea_id(self, self.fea_str, model_type)
        self.fea_value = 1

    def extract_fea_str(self, dependlist, argvlist, fea_name, slot):
        if len(dependlist) == 0:
            print >> sys.stderr, 'len(dependlist) == 0'
            sys.exit()
        self.fea_str = "%s,%s" %(fea_name, "-".join(dependlist))
        self.fea_value = 1

    def call_stat_info(self,dependlist,argvlist,slot, label):
        if len(dependlist) == 0:
            print >> sys.stderr, 'len(dependlist) == 0'
            sys.exit()
        fea_str = "%s-%s" %(slot, "-".join(dependlist))
        fea_extract_root.stat_info(self, fea_str, label)

    def get_id_dict(self):
        return fea_extract_root.get_id_dict(self)

