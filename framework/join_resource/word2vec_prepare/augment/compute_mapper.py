#!/home/work/local/python-2.7/bin/python
import sys
import urllib

def mapper():
    showdict = {}
    clickdict = {}
    pricedict = {}
    for line in sys.stdin:
        if not line:
            break
        line = line.strip('\n')
        if line == "":
            continue
        data = line.split("\t")

        cmatch = data[9];
        target_url = "";
        
        if cmatch == "204" or cmatch == "225" or cmatch == "201":
            target_url = urllib.unquote(data[73])
        elif cmatch == "222" or cmatch == "223" or cmatch == "228" or cmatch == "229":
            target_url = urllib.unquote(data[92])
        else:
            continue;

        if len(target_url) <= 2 or target_url.isdigit() or len(target_url.split("\t")) != 1:
            continue

        query = urllib.unquote(data[3]).replace("\t", " ").strip()
        bidword = urllib.unquote(data[23]).replace("\t", " ").strip()
        if len(query) == 0:
            continue
        key = target_url + "\t" + query
       
        showdict[key] = showdict.get(key, 0) + int(data[0])
        clickdict[key] = clickdict.get(key, 0) + int(data[1])
        pricedict[key] = pricedict.get(key, 0) + int(data[2])
    
    for key in showdict:
        print "%s\t%s\t%s\t%s" %(key, clickdict[key], showdict[key], pricedict[key])

if __name__ == "__main__":
    mapper();
