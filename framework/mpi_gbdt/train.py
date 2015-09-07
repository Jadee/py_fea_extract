import sys
import os

def mapper():
    for line in sys.stdin:
        if not line:
            continue

        line = line.strip('\n')
        data = line.split("\t")

        part = data[0].split(" ")
        instance = []
        instance.append(part[0])
        instance.append(part[1])
        length = len(part)
        
        for idx in xrange(2, length):
            tmp = part[idx].split(":")
            #if tmp[1] == "-1":
            #continue
            instance.append(part[idx])
        print " ".join(instance)


if __name__ == "__main__":
    mapper()
#print os.system(cmd)[0]
