#!/bin/env python
import sys
import time

sys.path.append("adfea_py_src")

from adfea_py_src.features.FeaExtractFrame import *

fea_dict = {}

def main(model_type):
    if len(sys.argv) < 3:
        fea_sign_filename = ""
        fea_ins_sign_filename = ""
    else:
        fea_sign_filename = sys.argv[2]
        fea_ins_sign_filename = sys.argv[3]
        
    fea_common_conf_filename = "./adfea_py_conf/af_parse.conf"
    fea_list_conf_filename = "./adfea_py_conf/featurelist.conf"
    fe_extract_manager = fea_extract_manage(fea_common_conf_filename,fea_list_conf_filename, fea_sign_filename,fea_ins_sign_filename)
    fe_extract_manager.initialize()
    for line in sys.stdin:
        if not line:
            continue
        line = line.strip('\n')
        if len(line) == 0:
            continue
        
        if fea_dict.has_key(line):
            fea_value = fea_dict[line]
            part = fea_value.split(" ")
            weight = part[0]
            label = part[1]
            to_print = part[2:]
            output = " ".join(to_print)
            if len(output) == 0:
                continue
            print "%s %s %s#A" % (weight, label, output)
        else:
            fe_extract_manager.generate_ins_str(line)
            ret_value = fe_extract_manager.print_ins_id()
            if ret_value != None:
                part = ret_value.split(" ")
                weight = part[0]
                label = part[1]
                to_print = part[2:]
                output = " ".join(to_print)
                if len(output) == 0:
                    continue
                print "%s %s %s#A" % (weight, label, output)
            fea_dict[line] = ret_value
        #print fe_extract_manager.get_ins_feastr_list(line)
    if model_type == "train":
        fe_extract_manager.print_feastr_id()

     #print "finish"
     #print time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time())) 
if __name__=="__main__":
    main(sys.argv[1])
