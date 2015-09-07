#input: term \t vec \t url1 freq1 \t url2 freq2
#output: url \t vec \t freq

import sys

for line in sys.stdin:
    flds = line.strip().split("\t");
    vec = flds[1];
    for ele in flds[2:]:
        data = ele.split(' ');
        if len(data) != 2:
            continue;
        print data[0] + "\t" + vec + "\t" + data[1];



