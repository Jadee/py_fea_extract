import sys

def mapper():
    queryDict = {};
    for line in sys.stdin:
        if not line:
            continue;
        
        data = line.strip().split('\t');
        
        if len(data) < 17:
            continue;
        
        if data[17][0:19] == "http://v.baidu.com/" and len(data[16]) > 4:
            query = data[16];
            queryDict[query] = queryDict.get(query, 0) + 1;
            
    for k,v in queryDict.items():
        print k + "\t" + str(v);


def reduce():
    preQuery = "";
    preFreq = 0;

    for line in sys.stdin:
        if not line:
            continue;

        data = line.strip().split('\t');
    
        if len(data) != 2:
            continue;
   
        query = data[0];
        freq = int(data[1]);
    
        if query != preQuery and preQuery != "":
            print preQuery + "\t" + str(preFreq);
            preFreq = 0;
    
        preQuery = query;
        preFreq += freq;
        
    print preQuery + "\t" + str(preFreq);


if __name__ == "__main__":
    if sys.argv[1] == "mapper":
        mapper()
    else:
        reduce()
