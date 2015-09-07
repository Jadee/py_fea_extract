import sys

if len(sys.argv) != 4:
    print "Usage:\n\tpython this.py dict.txt newDict lines_to_merge"

TVDict = {}
for line in open(sys.argv[1], 'r'):
    if not line:
        continue;
    data = line.strip().split('\t');
    TVDict[data[0]] = 1;
    
    
cnt = 0;
for line in open(sys.argv[2], 'r'):
    if not line:
        continue;
    cnt += 1;
    if cnt > int(sys.argv[3]):
        break;
    data = line.strip().split('\t');
    TVDict[data[0]] = 1;

f = open(sys.argv[1], 'w');
for k in TVDict.keys():
    print >>f, k; 
    
    
