
import sys
import random


print "weight\tlabel\tpredict_value\tkey\tsource\tshow\tclick\tprice\twinfoid\tuserid\tbidword\ttitle\tdesc1\tmt_id\ttarget_url"
for line in sys.stdin:
    if not line:
        break
    line = line.strip()
    data = line.split("\t")

    show = int(data[6])
    for idx in xrange(0, show):
        ran = random.random()
        if ran > 0.99982:
            print line
            continue
            out = data[2] + "\t" + data[3] + "\t" + data[4] + "\t" + data[8] + "\t" + data[9]
            out += "\t" + data[10] + "\t" + data[11] + "\t" + data[12] + "\t" + data[13] + "\t" + data[14]
            print out
        
