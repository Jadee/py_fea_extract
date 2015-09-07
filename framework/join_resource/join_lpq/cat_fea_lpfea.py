# -*- coding: gbk -*-
# Written by Wei chao, 2013/10/15
# This program is used as either a mapper or a reducer
# to cat landing page features and other features

# mapper: add a key (url+0) if input line is about other features
# e.g. before-->feature1\tfeature2\tfeature3...
#      after -->url\t0\tfeature1\tfeature2\tfeature3...

#         add a key (url+1) if input line is about lp features
# e.g. before-->feature1\tfeature2\tfeature3...
#      after -->url\t1\tfeature1\tfeature2\tfeature3...


# reducer: cat input lines (consecutive input lines should 
#           begin with the same url but different 0 or 1)
# e.g. before-->url\t0\tfeature\tfeature\tfeature...
#               url\t1\tfeature\tfeature\tfeature...
#      NOTE!! The first feature in line2 should be url
#             and be deleted when catting!
#      after -->feature\tfeature\t...

import sys
import ConfigParser
import urllib

def mapper(conf_filename):
    '''@desc log 拼接landing page 特征 为不同资源打上tag'''
    url_position = -1;

    config = ConfigParser.ConfigParser()
    config.readfp(open(conf_filename, "r"))

    field_list = config.get("after_parse_field", "af_map_output_key")
    fea_column = field_list.split(",")
    fea_column_len = len(fea_column)

    for i in xrange(0, fea_column_len):
        if fea_column[i] == 'target_url':
            url_position = i;
            break;
        else:
            pass;

    if url_position == -1:
        return None;

    for line in sys.stdin:
        if not line:
            continue;
        line = line.strip('\n')
        data = line.split("\t")

        if len(data) == fea_column_len:
            url = urllib.unquote(data[url_position])
            print "%s\t2\t%s" %(url, line)
        else:
            print line
                
def reducer(conf_filename):
    '''@desc mapper的输出会按照url + tag 进行排序 '''
    '''@desc 资源拼接'''
    last_url = ""
    
    config = ConfigParser.ConfigParser()
    config.readfp(open(conf_filename, "r"))

    lpq_fea_items = config.items("lpq_fea_resource")
    lpq_intent_items = config.items("lpq_intent_resource")

    fea_len = len(lpq_fea_items)
    intent_len = len(lpq_intent_items)

    fea_out = []
    for i in xrange(0, fea_len):
        fea_out.append("\N")
    intent_out = []
    for i in xrange(0, intent_len):
        intent_out.append("\N")

    lpq_fea = "\t".join(fea_out)         #landing 的基本特征（默认值为\N的字符串)
    lpq_plsa = "\t".join(intent_out)     #landing 的plsa 向量默认值为\N的字符串)

    for line in sys.stdin:
        if not line:
            continue;
        data = line.strip('\n').split("\t");

        length = len(data)

        cur_url = data[0]
        try:
            tag = int(data[1])
        except:
            continue

        to_print = []
        for idx in xrange(2, length):
            if data[idx] == "":
                to_print.append("\N")
            else:
                to_print.append(data[idx])
        
        if tag == 0:
            lpq_plsa = "\t".join(intent_out)
            lpq_fea = "\t".join(to_print)
        elif tag == 1:
            if cur_url != last_url:
                lpq_fea = "\t".join(fea_out)
            lpq_plsa = "\t".join(to_print)

        elif tag == 2:
            output = "\t".join(to_print)

            if cur_url != last_url:
                lpq_fea = "\t".join(fea_out)
                lpq_plsa = "\t".join(intent_out)

            print "%s\t%s\t%s" %(output, lpq_fea, lpq_plsa)
        last_url = cur_url

if __name__ == "__main__":
    if sys.argv[1] == "mapper":
        mapper(sys.argv[2]);
    elif sys.argv[1] == "reduce":
        reducer(sys.argv[2])
    else:
        sys.exit(0)
