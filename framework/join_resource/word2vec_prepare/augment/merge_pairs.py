import sys

preKey = "";
preClickCnt = 0.0;
preShwCnt = 0.0;
prePriceCnt = 0.0

for line in sys.stdin:
    if not line:
        continue;
    
    line = line.strip('\n');
    data = line.split('\t');

    if len(data) != 6:
        continue;
    key = data[0] + "\t" + data[1];
    
    if key != preKey and preKey != "":
        print preKey + "\t" + str(preClickCnt) + "\t" + str(preShwCnt) + "\t" + str(preClickCnt/preShwCnt) + "\t" + str(prePriceCnt);
        preClickCnt = 0.0;
        preShwCnt = 0.0;
        prePriceCnt = 0.0

    preKey = key;
    preClickCnt += float(data[2]);
    preShwCnt += float(data[3])
    prePriceCnt += float(data[5]);

if preKey != "":
   print preKey + "\t" + str(preClickCnt) + "\t" + str(preShwCnt) + "\t" + str(preClickCnt/preShwCnt) + "\t" + str(prePriceCnt); 
