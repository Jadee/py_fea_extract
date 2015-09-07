# -*- coding: gbk -*-

import sys
import ConfigParser

def mapper(conf_filename):
    winfoid_index = -1
    config = ConfigParser.ConfigParser()
    config.readfp(open(conf_filename, "r"))
    field_list = config.get("fea_extract_input_field", "schema")
    fea_column = field_list.split(",")
    fea_column_len = len(fea_column)

    for i in xrange(0, fea_column_len):
        if fea_column[i] == 'winfoid':
            winfoid_index = i
            break
        else:
            continue
    if winfoid_index == -1:
        return None

    for line in sys.stdin:
        if not line:
            continue
        line = line.strip()
        data = line.split("\t")

        if len(data) == fea_column_len:
            winfoid = data[winfoid_index]
            print "%s\t1\t%s" %(winfoid, line)
        else:
            winfoid = data[0]
            word2vec_sim = data[1]
            print "%s\t0\t%s" %(winfoid, word2vec_sim)

def reduce():
    '''@desc mapper的输出会按照winfoid + tag 进行排序 '''
    '''@desc 资源拼接'''
    last_winfoid = ""
    word2vec_sim = "-1"
    for line in sys.stdin:
        if not line:
            continue
        data = line.strip('\n').split("\t");
        length = len(data)

        cur_winfoid = data[0]
        try:
            tag = int(data[1])
        except:
            continue

        if tag == 0:
            word2vec_sim = data[2]
        else:
            to_print = []
            for idx in xrange(2, length):
                to_print.append(data[idx])
        
            if cur_winfoid == last_winfoid:
                print "%s\t%s" %("\t".join(to_print), word2vec_sim)
            else:
                print "%s\t-1" %("\t".join(to_print))

        last_winfoid = cur_winfoid
        
if __name__ == "__main__":
    if sys.argv[1] == "mapper":
        mapper(sys.argv[2])
    else:
        reduce()
