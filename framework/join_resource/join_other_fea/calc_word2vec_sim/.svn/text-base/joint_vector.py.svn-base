# -*- coding: gbk -*-

import sys
import urllib
import math

import process_str

sys.path.append('seg_word')
from seg_word import wordrank_ecom

# mapper input: 
#   1. winfoid \t tag(2) \t bidword \t target_url
#   2. term \t tag(0) \t vector
#   3. url  \t tag(1) \t vector
# mapper output:
#   1. term \t tag(0) \t vector
#   2. term \t tag(1) \t term_info \t winfoid
#   3. url  \t tag(0) \t vector
#   4. url  \t tag(1) \t url_info \t winfoid
def mapper():
    seg_path = './dict_seg_wordrank/worddict/'
    tag_path = './dict_seg_wordrank/tagdict/'
    ner_path = './dict_seg_wordrank/wordner.conf'
    stop_words_path = "./dict_seg_wordrank/stop_words.txt"
    seg_handle = wordrank_ecom.Seg_Rank();
    seg_handle.seg_dict_init(seg_path, tag_path, ner_path, stop_words_path);

    for line in sys.stdin:
        if not line:
            continue
        line = line.strip()
        data = line.split("\t")

        length = len(data)
        if length == 3:
            tag = data[1]
            if tag == "0":    #word vector dict
                term = process_str.handle_str(data[0]).strip()
                if len(term) == 0:
                    continue
                vec = data[2].strip().split(' ');
                sum = 0
                for ele in vec:
                    sum = sum + float(ele) * float(ele);
                sum = math.sqrt(sum);
                vec = [str(float(x)/sum) for x in vec];
                print "%s\t0\t%s" %(term, " ".join(vec))
            elif tag == "1":  #url vector dict
                print "%s\t0\t%s" %(data[0], data[2])
            else:
                continue
        else:
            if data[1] != "2":
                continue
            winfoid = data[0];
            bidword = data[2];

            for idx in xrange(3, len(data)):
                target_url = data[idx]
                print "%s\t1\turl_info\t%s" %(target_url, winfoid)

            if len(bidword) == 0:
                continue
            try:
                (ret, token, netoken) = seg_handle.get_seg(bidword);
                if ret < 0:
                    continue

                for term, postag in token:
                    term = term.strip()
                    if len(term) == 0:
                        continue
                    print "%s\t1\tterm_info\t%s" %(term, winfoid)
            except:
                continue

# reduce input: 
#   1. term \t tag(0) \t vector
#   2. term \t tag(1) \t term_info \t winfoid
#   3. url  \t tag(0) \t vector
#   4. url  \t tag(1) \t url_info \t winfoid
# reduce output:
#   1. winfoid \t term \t vector \t term_info
#   2. winfoid \t url  \t vector \t url_info
def reduce():
    pre_key =""
    value = ""
    for line in sys.stdin:
        if not line:
            continue
        line = line.strip()
        data = line.split("\t")

        if len(data) != 3 and len(data) != 4:
            continue
        
        key = data[0]
        tag = data[1]

        if tag == "0":
            value = data[2]
        elif tag == "1":   #url data
            value_name = data[2]
            winfoid = data[3]

            if value_name == "term_info":
                term_vector = "NULL"
                if key == pre_key:
                    term_vector = value
                    print "%s\t%s\t%s\tterm_info" %(winfoid, key, term_vector)
            if value_name == "url_info":
                url_vector = "NULL"
                if key == pre_key:
                    url_vector = value
                    print "%s\t%s\t%s\turl_info" %(winfoid, key, url_vector)
        else:
            continue
        
        pre_key = key
            
if __name__ == "__main__":
    if sys.argv[1] == "mapper":
        mapper()
    else:
        reduce()
