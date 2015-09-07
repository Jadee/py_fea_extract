#!/bin/env python  
# -*- coding: gbk -*-

import sys
import urllib
import ConfigParser
import math
import os

import logging
import process_str
from adfea_py_src.seg_word import wordrank_ecom

class seg_wordrank():

    seg_result_buff = {}

    def __init__(self):

        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open("./adfea_py_conf/adfea_py.conf", "rb"))

        self.seg_path = self.config.get("seg_word", "seg_path")
        self.tag_path = self.config.get("seg_word", "tag_path")
        self.ner_path = self.config.get("seg_word", "ner_path")
        self.stop_words_path = self.config.get("seg_word", "stop_words_path")

        try:
            self.dict_buff = int(self.config.get("seg_word_dict_buff", "buffer"))
        except:
            self.dict_buff = 10240

        self.seg_handle = wordrank_ecom.Seg_Rank()
        self.seg_handle.seg_dict_init(self.seg_path, self.tag_path, self.ner_path, self.stop_words_path)


    def __del__(self):
        self.seg_handle.seg_dict_close()

    def seg_word(self, word):

        if len(word) == 0:
            emlist = []
            return emlist

        if len(word) > 512:
            word = word[0:512]

        if seg_wordrank.seg_result_buff.has_key(word):
            return seg_wordrank.seg_result_buff[word]
        else:
            seglist = []
            try:
                (ret, token, netoken) = self.seg_handle.get_seg(word)
                if ret < 0:
                    seglist.append(word)
                else:
                    term_count = 0
                    for term, postag in token:
                        if term_count > 128:
                            break
                        term_count += 1
                        try:
                            if type(eval(term)) == float:
                                continue
                            if type(eval(term)) == int:
                                continue
                            seglist.append(term)
                        except:
                            seglist.append(term)

                if len(seg_wordrank.seg_result_buff) < self.dict_buff:
                    seg_wordrank.seg_result_buff[word] = seglist
                return seglist
            except:
                return seglist

seg_rank = seg_wordrank()
trade_cos_dict = {}
def read_trade_cos_sim():
    config = ConfigParser.ConfigParser()
    config.readfp(open("./adfea_py_conf/adfea_py.conf", "rb"))
    trade_cos_pzd_path = config.get("trade_cos_pzd", "path")
    trade_cos_pzd_file = open(trade_cos_pzd_path, "r")

    for line in trade_cos_pzd_file:
        if not line:
            continue
        data = line.strip().split("\t")
        if len(data) < 3:
            continue
        key = data[0] + "," + data[1]
        trade_cos_dict[key] = data[2]
    trade_cos_pzd_file.close()

trade_plsa_pzd_dict = {}
def read_trade_plsa_pzd():
    config = ConfigParser.ConfigParser()
    config.readfp(open("./adfea_py_conf/adfea_py.conf", "rb"))
    trade_plsa_pzd_path = config.get("trade_plsa_pzd", "path")
    trade_plsa_pzd_file = open(trade_plsa_pzd_path, "r")

    for line in trade_plsa_pzd_file:
        if not line:
            continue
        data = line.strip().split("\t")
        length = len(data)
        if length <= 6:
            continue
        key = data[0]
        printlist = []
        idx = 6
        while idx < length:
            out = data[idx] + ":" + data[idx + 1]
            printlist.append(out)
            idx += 2
        trade_plsa_pzd_dict[key] = ",".join(printlist)
    trade_plsa_pzd_file.close()

VECTOR_SIZE = 300
latent_relevance_model_dict = VECTOR_SIZE * VECTOR_SIZE * [0];
def read_latent_relevance_model():
    config = ConfigParser.ConfigParser()
    config.readfp(open("./adfea_py_conf/adfea_py.conf", "rb"))
    latent_relevance_model_path = config.get("latent_relevance_model", "path")
    latent_relevance_model_file = open(latent_relevance_model_path, "r")

    index = 1
    for line in latent_relevance_model_file:
        if not line:
            continue
        line = line.strip()
        if index >= 7:
            latent_relevance_model_dict[index - 7] = float(line)
        index += 1
    latent_relevance_model_file.close()
    
read_trade_cos_sim()
read_trade_plsa_pzd()
read_latent_relevance_model()
    
class Extractor_seg_word():
    plsa_pzd_buffer = {}

    avg_bidword_length = 13   #average of bidword
    avg_bidword_term = 4      #average of terms of bidword
    
    def __init__(self):
        pass
    def __del__(self):
        pass

    def str2word(self, sen):
        global seg_rank
        data = sen.split(",")
        wdlist = []
        wtlist = []
        length = len(data)
        for idx in xrange(0, length):
            word = process_str.handle_str(data[idx])
            if word == "":
                continue
            tmp = seg_rank.seg_word(word)
            for wd in tmp:
                wdlist.append(wd)

        wtlist = []
        length = len(wdlist)
        for i in xrange(0, length):
            wtlist.append(1)
        senlist = []
        senlist.append(wdlist)
        senlist.append(wtlist)
        return senlist

    # term1:weight1,term2,weight2 数据解析
    def specialSen2word(self, sen):
        wdlist = []
        wtlist = []
        data = sen.split(",")
        length = len(data)
        for idx in xrange(0, length):
            part = data[idx].split(":")
            wdlist.append(part[0])
            wtlist.append(part[1])
        senlist = []
        senlist.append(wdlist)
        senlist.append(wtlist)
        return senlist

    def s_term_num(self, dependlist):
        '''@desc 切词个数 '''
        num = 0
        for word in dependlist:
            word = urllib.unquote(word.strip())
            if word == "":
                num += 0
            else:
                num += len(self.str2word(word)[0])
        return num

    def s_match_term_num(self, dependlist, argvlist):
        '''@desc 参数1和参数2切词后，参数1在参数2中的匹配个数'''
        if len(dependlist) != 2:
            return -1
        sentence1 = urllib.unquote(dependlist[0].strip())
        sentence2 = urllib.unquote(dependlist[1].strip())
        if len(sentence1) == 0 or len(sentence2) == 0:
            return -1
        if sentence1 == "\N" or sentence2 == "\N":
            return -1

        word1_list = self.str2word(sentence1)[0]
        word2_list = self.str2word(sentence2)[0]

        word1_num = len(word1_list)
        word2_num = len(word2_list)
        
        if word1_num == 0 or word2_num == 0:
            return 0

        match_num = 0
        for term in word1_list:
            if term in word2_list:
                match_num += 1
                
        all_list = word1_list + word2_list
        all_list = {}.fromkeys(all_list).keys()
    
        if len(argvlist) == 0:
            argv = 0
        else:
            try:
                argv = int(argvlist[0])
            except:
                argv = 0
        
        if argv == 0:
            return match_num
        elif argv == 1:
            return float(match_num) / float(word1_num)
        elif argv == 2:
            return float(match_num) / float(word2_num)
        elif argv == 3:         #a b 交集 / a b 并集
            return float(match_num) / float(len(all_list))
        else:
            return match_num

    def s_uniq_match_term_num(self, dependlist, argvlist):
        '''@desc 参数1和参数2切词后，参数1(去重后)在参数2中的匹配个数'''
        if len(dependlist) != 2:
            return -1
        sentence1 = urllib.unquote(dependlist[0].strip())
        sentence2 = urllib.unquote(dependlist[1].strip())
        if len(sentence1) == 0 or len(sentence2) == 0:
            return -1
        if sentence1 == "\N" or sentence2 == "\N":
            return -1

        word1_list = self.str2word(sentence1)[0]
        word2_list = self.str2word(sentence2)[0]

        word1_num = len(word1_list)
        word2_num = len(word2_list)
        if word1_num == 0 or word2_num == 0:
            return 0

        dup_word2_list = {}.fromkeys(word2_list).keys()
        word2_num = len(dup_word2_list)
        match_num = 0
        for term in word1_list:
            if term in dup_word2_list:
                match_num += 1
        
        all_list = word1_list + dup_word2_list
        all_list = {}.fromkeys(all_list).keys()     # a b 并集
    
        if len(argvlist) == 0:
            argv = 0
        else:
            try:
                argv = int(argvlist[0])
            except:
                argv = 0
            
        if argv == 0:
            #return 匹配个数
            return match_num
        elif argv == 1:
            #return 匹配term数在参数1中的占比
            return float(match_num) / float(word1_num) / float(Extractor_seg_word.avg_bidword_term)
        elif argv == 2:
            #return 匹配term数在参数2中的占比
            return float(match_num) / float(word2_num) / float(Extractor_seg_word.avg_bidword_term)
        elif argv == 3:
            return float(match_num) / float(len(all_list))
        else:
            return match_num

    def s_match_term_length(self, dependlist, argvlist):
        '''@desc 参数1和参数2切词后，参数1在参数2中的匹配term数的长度'''
        if len(dependlist) != 2:
            return -1
        sentence1 = urllib.unquote(dependlist[0].strip())
        sentence2 = urllib.unquote(dependlist[1].strip())
        if len(sentence1) == 0 or len(sentence2) == 0:
            return -1
        if sentence1 == "\N" or sentence2 == "\N":
            return -1

        word1_list = self.str2word(sentence1)[0]
        word2_list = self.str2word(sentence2)[0]

        if len(word1_list) == 0 or len(word2_list) == 0:
            return 0

        length1 = 0
        for term in word1_list:
            length1 += len(term)
        length2 = 0
        for term in word2_list:
            length2 += len(term)
        match_length = 0
        for term in word1_list:
            if term in word2_list:
                match_length += len(term)
        
        all_list = word1_list + word2_list
        all_list = {}.fromkeys(all_list).keys()
        all_length = 0
        for term in all_list:
            all_length = len(term)
    
        if len(argvlist) == 0:
            argv = 0
        else:
            try:
                argv = int(argvlist[0])
            except:
                argv = 0
    
        if argv == 0:
            return match_length
        elif argv == 1:
            return float(match_length) / float(length1) / float(Extractor_seg_word.avg_bidword_length)
        elif argv == 2:
            return float(match_length) / float(length2) / float(Extractor_seg_word.avg_bidword_length)
        elif argv == 3:
            return float(match_length) / float(all_length)
        else:
            return match_length

    def s_uniq_match_term_length(self, dependlist, argvlist):
        '''@desc 参数1和参数2切词后，参数1在参数2中的匹配term数的长度'''
        if len(dependlist) != 2:
            return -1
        sentence1 = urllib.unquote(dependlist[0].strip())
        sentence2 = urllib.unquote(dependlist[1].strip())
        if len(sentence1) == 0 or len(sentence2) == 0:
            return -1
        if sentence1 == "\N" or sentence2 == "\N":
            return -1

        word1_list = self.str2word(sentence1)[0]
        word2_list = self.str2word(sentence2)[0]

        word2_list = {}.fromkeys(word2_list).keys()
    
        if len(word1_list) == 0 or len(word2_list) == 0:
            return 0

        length1 = 0
        for term in word1_list:
            length1 += len(term)
        length2 = 0
        for term in word2_list:
            length2 += len(term)
        match_length = 0
        
        for term in word1_list:
            if term in word2_list:
                match_length += len(term)
        
        all_list = word1_list + word2_list
        all_list = {}.fromkeys(all_list).keys()
        all_length = 0
        for term in all_list:
            all_length = len(term)
    
        if len(argvlist) == 0:
            argv = 0
        else:
            try:
                argv = int(argvlist[0])
            except:
                argv = 0
    
        if argv == 0:
            return match_length
        elif argv == 1:
            return float(match_length) / float(length1) / float(Extractor_seg_word.avg_bidword_length)
        elif argv == 2:
            return float(match_length) / float(length2) / float(Extractor_seg_word.avg_bidword_length)
        elif argv == 3:
            return float(match_length) / float(all_length)
        else:
            return match_length

    # longest_common_string   continue
    def midleI(self, i, firstStr, secondStr):
        str = []
        j = 0
        len_first = len(firstStr)
        len_second = len(secondStr)
        while i < len_first and j < len_second:
            while j < len_second and i < len_first:
                if firstStr[i] == secondStr[j]:
                    str.append(secondStr[j])
                    i += 1
                j += 1
        return str

    # term weidu
    def s_longest_common_string(self, dependlist, argvlist):
        '''@desc 最长公共子串 '''
        if len(dependlist) != 2:
            return -1
        sentence1 = urllib.unquote(dependlist[0].strip())
        sentence2 = urllib.unquote(dependlist[1].strip())
        if len(sentence1) == 0 or len(sentence2) == 0:
            return -1
        if sentence1 == "\N" or sentence2 == "\N":
            return -1

        wordlist1 = self.str2word(sentence1)[0]
        wordlist2 = self.str2word(sentence2)[0]

        word1_num = len(wordlist1)
        word2_num = len(wordlist2)
        if word1_num == 0 or word2_num == 0:
            return 0
        word2_len = 0
        for term in wordlist2:
            word2_len += len(term)
        word1_len = 0
        for term in wordlist1:
            word1_len += len(term)
    
        sen = []
        term_num = 0
        term_len = 0
        result = []
        lenId = 0
        length = len(wordlist1)
        for i in xrange(0, length):
            result = self.midleI(i, wordlist1, wordlist2)
            sen.append(result)
            temp_len = 0
            for term in result:
                temp_len += len(term)
                #temp_len += len(unicode(term, 'gb2312', 'ignore'))
            if len(result) > term_num or temp_len > term_len:
                term_num = len(result)
                term_len = temp_len
                lenId = i
        ls = sen[lenId]

        if len(argvlist) == 0:
            argv = 0
        else:
            try:
                argv = int(argvlist[0])
            except:
                argv = 0
        
        if argv == 0:
            return term_num     # term number
        elif argv == 1:    # term length
            return term_len
        elif argv == 2:    # term number zhanbi
            return float(term_num) / float(word1_num) / float(Extractor_seg_word.avg_bidword_term)
        elif argv == 3:    # term length zhanbi
            return float(term_len) / float(word1_len) / float(Extractor_seg_word.avg_bidword_term)
            #return float(term_len) / float(len(unicode(sentence2, 'gb2312', 'ignore')))
        elif argv == 4:
            return float(term_num) / float(word2_num) / float(Extractor_seg_word.avg_bidword_term)
        elif argv == 5:
            return float(term_len) / float(word2_len) / float(Extractor_seg_word.avg_bidword_term)
        else:
            return term_num

    def s_longest_common_string_uncontinue(self, dependlist, argvlist):
        '''@desc 最长公共子序列'''
        if len(dependlist) != 2:
            return -1
        sentence1 = urllib.unquote(dependlist[0].strip())
        sentence2 = urllib.unquote(dependlist[1].strip())
        if len(sentence1) == 0 or len(sentence2) == 0:
            return -1
        if sentence1 == "\N" or sentence2 == "\N":
            return -1

        wordlist1 = self.str2word(sentence1)[0]
        wordlist2 = self.str2word(sentence2)[0]

        word1_num = len(wordlist1)
        word1_len = len(sentence1)
        word2_num = len(wordlist2)
        word2_len = len(sentence2)

        if word1_num == 0 or word2_num == 0:
            return 0

        if len(wordlist1) > len(wordlist2):
            wordlist1, wordlist2 = wordlist2, wordlist1

        length1 = len(wordlist1) + 1
        length2 = len(wordlist2) + 1
        matrix = [range(length2) for x in range(length1)]
        flag = [range(length2) for x in range(length1)]

        for m in xrange(0, length1):
            matrix[m][0] = 0
        for k in xrange(1, length2):
            matrix[0][k] = 0
 
        for i in xrange(1, length1):
            for j in xrange(1, length2):
                if wordlist1[i-1] == wordlist2[j-1]:
                    matrix[i][j] = matrix[i-1][j-1] + 1
                    flag[i][j] = 1
                elif matrix[i][j - 1] > matrix[i - 1][j]:
                    matrix[i][j] = matrix[i][j - 1]
                    flag[i][j] = 2
                else:
                    matrix[i][j] = matrix[i - 1][j]
                    flag[i][j] = 3
                #matrix[i][j] = max(matrix[i-1][j], matrix[i][j-1])
   
        #result = []
        i = length1 - 1
        j = length2 - 1
        term_len = 0
        while i > 0 and j > 0:
            if flag[i][j] == 1:
                term_len += len(wordlist1[i - 1])
                #term_len += len(unicode(wordlist1[i-1], 'gb2312', 'ignore'))
                #result.append(wordlist1[i-1])
                i -= 1
                j -= 1
            elif flag[i][j] == 3:  #matrix[i - 1][j] == matrix[i][j - 1]:
                i -= 1
            elif flag[i][j] == 2:
                j -= 1

        term_num = matrix[length1 - 1][length2 - 1]

        if len(argvlist) == 0:
            argv = 0
        else:
            try:
                argv = int(argvlist[0])
            except:
                argv = 0
        
        if argv == 0:       #term_num
            return term_num
        elif argv == 1:     #term_length
            return term_len
        elif argv == 2:     #term_num zhanbi
            return float(term_num) / float(word1_num) / float(Extractor_seg_word.avg_bidword_term)
        elif argv == 3:     #term_length zhanbi
            return float(term_len) / float(word1_len) / float(Extractor_seg_word.avg_bidword_length)
            #return float(term_len) / float(len(unicode(sentence2, 'gb2312', 'ignore')))
        elif argv == 4:     #term_num zhanbi
            return float(term_num) / float(word2_num) / float(Extractor_seg_word.avg_bidword_term)
        elif argv == 5:
            return float(term_len) / float(word2_len) / float(Extractor_seg_word.avg_bidword_length)
        else:
            return term_num

    def s_edit_distance(self, dependlist):
        '''@desc 编辑距离'''
        if len(dependlist) != 2:
            return -1
        sentence1 = urllib.unquote(dependlist[0].strip())
        sentence2 = urllib.unquote(dependlist[1].strip())
        if len(sentence1) == 0 or len(sentence2) == 0:
            return -1
        if sentence1 == "\N" or sentence2 == "\N":
            return -1

        wordlist1 = self.str2word(sentence1)[0]
        wordlist2 = self.str2word(sentence2)[0]

        if len(wordlist1) == 0 or len(wordlist2) == 0:
            return 0

        if len(wordlist1) > len(wordlist2):
            wordlist1,wordlist2 = wordlist2,wordlist1
        if len(wordlist1) == 0:
            return len(wordlist2)
        if len(wordlist2) == 0:
            return len(wordlist1)

        first_length = len(wordlist1) + 1
        second_length = len(wordlist2) + 1
        distance_matrix = [range(second_length) for x in range(first_length)]
        
        for i in xrange(1, first_length):
            for j in xrange(1, second_length):
                deletion = distance_matrix[i - 1][j] + 1
                insertion = distance_matrix[i][j - 1] + 1
                substitution = distance_matrix[i - 1][j - 1]
                if wordlist1[i - 1] != wordlist2[j - 1]: 
                    substitution += 1
                distance_matrix[i][j] = min(insertion,deletion,substitution)
        #print distance_matrix
        return distance_matrix[first_length - 1][second_length - 1]

    def s_similarity(self, dependlist):
        '''@desc s = lc/(led + lc) lc最长公共子串的长度'''
        '''@desc led为编辑距离'''
        argvlist = []
        argvlist.append("0")
        lcs = self.s_longest_common_string(dependlist, argvlist)
        led = self.s_edit_distance(dependlist)
 
        if (led + lcs) == 0:
            return 0

        sim = float(lcs) / float(led + lcs)
        return sim

    def tid_ptr2dict(self, srcStr):
        """transfer pzd vector to dict, key is top-id, value is ptr"""
        tidptr_dict = {}
        data = srcStr.strip().split(",")
        if len(data) <= 0:
            return tidptr_dict
        tid_num = len(data)
        for tid_idx in xrange(0, tid_num):
            part = data[tid_idx].split(":")
            if len(part) == 2:
                try:
                    tidptr_dict[part[0]] = float(part[1])
                except:
                    continue
        return tidptr_dict

    def s_cos_dict(self, dependlist, argvlist):
        """calculate sim of two vecters""" 
        if len(dependlist) != 2:
            return -1
        sentence1 = urllib.unquote(dependlist[0].strip())
        if argvlist[0] == "user_trade":
            if trade_plsa_pzd_dict.has_key(dependlist[1]):
                sentence2 = trade_plsa_pzd_dict[dependlist[1]]   
            else:
                return -1
        else:
            sentence2 = urllib.unquote(dependlist[1].strip())

        if len(sentence1) == 0 or len(sentence2) == 0:
            return -1
        if sentence1 == "\N" or sentence2 == "\N":
            return -1

        dict1 = self.tid_ptr2dict(sentence1)
        dict2 = self.tid_ptr2dict(sentence2)
        sum1 = 0
        sum2 = 0
        inner_prod = 0

        for key in dict1.keys():
            if dict2.has_key(key):
                inner_prod += dict1[key] * dict2[key]
            sum1 += dict1[key] * dict1[key]
        for key in dict2.keys():
            sum2 += dict2[key] * dict2[key]
        if 0 == sum1 or 0 == sum2:
            return 0
        m = math.sqrt(sum1) * math.sqrt(sum2)
        return inner_prod * 1.0 / m

    def s_match_industry(self, dependlist, argvlist):
        '''@desc bidword和user的行业是否匹配'''
        if len(dependlist) != 2:
            return -1
        if dependlist[0] == "\N" or dependlist[1] == "\N":
            return -1
        try:
            trade1 = int(dependlist[0])
            trade2 = int(dependlist[1])
        except:
            return -1

        if trade1 == 990101 or trade2 == 990101:
            return -1
        if trade1 == 0 or trade2 == 0:
            return -1

        if len(argvlist) == 0:
            argv = 0
        else:
            try:
                argv = int(argvlist[0])
            except:
                argv = 0

        if argv == 3:    #三级行业是否匹配
            cmp_trade1 = trade1
            cmp_trade2 = trade2
        elif argv == 2:  #二级行业是否匹配
            cmp_trade1 = trade1 / 100
            cmp_trade2 = trade2 / 100
        elif argv == 1:  #一级行业是否匹配
            cmp_trade1 = trade1 / 10000
            cmp_trade2 = trade2 / 10000
        else:
            cmp_trade1 = trade1
            cmp_trade2 = trade2

        if cmp_trade1 == cmp_trade2:
            return 1
        else:
            return 0

    def s_trade_cos_sim(self, dependlist, argvlist):
        '''@desc 两个行业间的cos相似度'''
        if len(dependlist) != 2:
            return -1
        if dependlist[0] == "\N" or dependlist[1] == "\N":
            return -1

        try:
            trade1 = int(dependlist[0])      #三级行业
            trade2 = int(dependlist[1])
        except:
            return -1

        if trade1 == 990101 or trade2 == 990101:
            return -1
        if trade1 == 0 or trade2 == 0:
            return -1

        trade1_1 = int(trade1 / 10000)   #一级行业
        trade2_1 = int(trade2 / 10000)

        trade1_2 = int(trade1 / 100)     #二级行业
        trade2_2 = int(trade2 / 100)

        if len(argvlist) == 0:
            argv = 8
        else:
            try:
                argv = int(argvlist[0])
            except:
                argv = 8
    
        if argv == 0:
            key = "%s,%s" %(trade1_1, trade2_1)
        elif argv == 1:
            key = "%s,%s" %(trade1_1, trade2_2)
        elif argv == 2:
            key = "%s,%s" %(trade1_1, trade2)
        elif argv == 3:
            key = "%s,%s" %(trade1_2, trade2_1)
        elif argv == 4:
            key = "%s,%s" %(trade1_2, trade2_2)
        elif argv == 5:
            key = "%s,%s" %(trade1_2, trade2)
        elif argv == 6:
            key = "%s,%s" %(trade1, trade2_1)
        elif argv == 7:
            key = "%s,%s" %(trade1, trade2_2)
        else:
            key = "%s,%s" %(trade1, trade2)

        if trade_cos_dict.has_key(key):
            return trade_cos_dict[key]
        else:
            return 0

    def gen_vec_represention(self, input_vec):
        part = input_vec.split(",")
        vector = VECTOR_SIZE * [0]
        mod = 0.0
        for idx in xrange(0, len(part)):
            tmp = part[idx].split(":")
            if len(tmp) < 2:
                continue
            index = int(tmp[0])
            value = float(tmp[1])
            vector[index] = value
            mod += abs(value * value)
        for idx in xrange(0, VECTOR_SIZE):
            vector[idx] = vector[idx] / math.sqrt(mod)
        return vector
            
    def s_latent_relevance_sim(self, dependlist, argvlist):
        if len(dependlist) != 2:
            return -1
        sentence1 = dependlist[0].strip()
        sentence2 = dependlist[1].strip()
        
        if sentence1 == "\N" or sentence2 == "\N":
            return -1
            
        try:
            vector1 = self.gen_vec_represention(sentence1)
            vector2 = self.gen_vec_represention(sentence2)
            cosine = 0.0

            for idx in xrange(0, VECTOR_SIZE):
                cosine += vector1[idx] * vector2[idx];

            sum_weight = cosine * latent_relevance_model_dict[0] + 0.5 * latent_relevance_model_dict[-1]
            for i in xrange(0, VECTOR_SIZE):
                if abs(vector1[i]) < 0.05:
                    continue
                for j in xrange(0, VECTOR_SIZE):
                    if abs(vector2[j]) < 0.05:
                        continue
                    if i == j:
                        continue
                    value = vector1[i] * vector2[j]
                    index = i * VECTOR_SIZE + j + 1 - 1
                    sum_weight += latent_relevance_model_dict[index] * value
            
            latent_relevance = 1 / (1 + math.exp(-1 * sum_weight));
            return latent_relevance
        except:
            return -1

            
    def s_plsa_sim(self, dependlist):
        '''@desc 两个文本间的相似度'''
        if len(dependlist) != 2:
            return -1
        sentence1 = urllib.unquote(dependlist[0].strip()).replace("\t", "")
        sentence2 = urllib.unquote(dependlist[1].strip()).replace("\t", "")
        if len(sentence1) == 0 or len(sentence2) == 0:
            return -1
        if sentence1 == "\N" or sentence2 == "\N":
            return -1

        plsa_pzd1 = ""
        plsa_pzd2 = ""

        if Extractor_seg_word.plsa_pzd_buffer.has_key(sentence1):
            plsa_pzd1 = Extractor_seg_word.plsa_pzd_buffer[sentence1]
        else:
            try:
                cmd = "sh compute_plsa_pzd.sh \"%s\"" %(sentence1)
                ret = os.popen(cmd)
                while 1:
                    line = ret.readline()
                    if line == "":
                        break
                    plsa_pzd1 = line.strip('\n')
                Extractor_seg_word.plsa_pzd_buffer[sentence1] = plsa_pzd1
            except:
                print >>sys.stderr, sentence1

        if Extractor_seg_word.plsa_pzd_buffer.has_key(sentence2):
            plsa_pzd2 = Extractor_seg_word.plsa_pzd_buffer[sentence2]
        else:
            try:
                cmd = "sh compute_plsa_pzd.sh \"%s\"" %(sentence2)
                ret = os.popen(cmd)
                while 1:
                    line = ret.readline()
                    if line == "":
                        break
                    plsa_pzd2 = line.strip('\n')
                Extractor_seg_word.plsa_pzd_buffer[sentence2] = plsa_pzd2
            except:
                print >>sys.stderr, sentence1

        if plsa_pzd1 == "" or plsa_pzd2 == "":
            return -1

        part1 = plsa_pzd1.split("\t")
        part2 = plsa_pzd2.split("\t")

        if len(part1) < 5 or len(part2) < 5:
            return -1
        if part1[4] == "0" or part2[4] == "0": 
            return -1

        dict1 = {}
        dict2 = {}
        tid_idx = 5
        length = len(part1)
        while tid_idx < length:
            dict1[part1[tid_idx]] = float(part1[tid_idx + 1])
            tid_idx += 2
        tid_idx = 5
        length = len(part2)
        while tid_idx < length:
            dict2[part2[tid_idx]] = float(part2[tid_idx + 1])
            tid_idx += 2

        sum1 = 0
        sum2 = 0
        inner_prod = 0
        for key in dict1.keys():
            if dict2.has_key(key):
                inner_prod += dict1[key] * dict2[key]
            sum1 += dict1[key] * dict1[key]
        for key in dict2.keys():
            sum2 += dict2[key] * dict2[key]
        if 0 == sum1 or 0 == sum2:
            return 0
        m = math.sqrt(sum1) * math.sqrt(sum2)
        return inner_prod * 1.0 / m
'''
if __name__ == "__main__":
    obj = Extractor_seg_word()

    list1 = []
    list1.append("人名我共和国")
    list1.append("中华人名共和国")
    print obj.s_match_term_num(list1)
    #print obj.s_match_term_length(list1, 2)

    te = seg_wordrank()

    for key in te.seg_result_buff:
        print key

    list = []

    list.append("人名我共和国其他中华其他人名其他共和国")
    list.append("中华人名共和国")

    obj2 = Extractor_common_string()
    print obj2.s_longest_common_string(list, 0)
     #print obj2.s_longest_common_string(list, 1)
     #print obj2.s_longest_common_string_uncontinue(list, 0)
     #print obj2.s_edit_distance(list)
     #print obj2.s_similarity(list)

    for key in te.seg_result_buff:
        print key
'''
