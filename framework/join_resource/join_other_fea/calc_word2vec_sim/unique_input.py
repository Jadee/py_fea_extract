# author : lizhangfeng
# date   : 2014-3-24
# input: winfoid \t tag \t cmatch \t wmatch \t bidword \t show \t click \t price \t url
# output: winfoid \t tag(2) \t bidword \t target_url
# This script will get unique winfoid

import sys
import urllib

import process_str

def mapper(model_type):
    winfo_dict = {}
    for line in sys.stdin:
        if not line:
            continue
        flds = line.strip().split("\t");
    
        winfoid = flds[0];
        cmatch = flds[2];
        if cmatch == "204" or cmatch == "225" or cmatch == "201":
            target_url = flds[8];
        elif cmatch == "222" or cmatch == "223" or cmatch == "228" or cmatch == "229":
            target_url = flds[8];
        else:
            continue

        if len(target_url.split("\t")) != 1 or target_url == "" or target_url.isdigit():
                continue
        bidword = flds[4]
        if len(bidword) == 0:
            continue
        key = winfoid + "\t" + target_url
        if winfo_dict.has_key(key) == True:
            continue
        winfo_dict[key] = 1
        print "%s\t2\t%s\t%s" % (winfoid, bidword, target_url);

def reduce():
    pre_key = ""

    url_dict = {}
    for line in sys.stdin:
        if not line:
            continue
        flds = line.strip().split("\t");

        if len(flds) < 4:
            continue

        key = flds[0] + "\t" + flds[1] + "\t" + flds[2];

        if key != pre_key and pre_key != "":
            url_out = "\t".join(url_dict.keys())
            if url_out != "":
                print "%s\t%s" %(pre_key, url_out)
            url_dict.clear()

        pre_key = key;
        url_dict[flds[3]] = 1
        
    url_out = "\t".join(url_dict.keys())
    if url_out != "":
        print "%s\t%s" %(pre_key, url_out)

if __name__ == "__main__":
    if sys.argv[1] == "mapper":
        mapper(sys.argv[2])
    else:
        reduce()


