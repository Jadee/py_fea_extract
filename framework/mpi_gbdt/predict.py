import sys
import os
import urllib

def mapper():
    pre_dict = {}
    for line in sys.stdin:
        if not line:
            continue

        line = line.strip('\n')
        data = line.split("\t")
        to_print = []

        if pre_dict.has_key(data[0]):
            to_print.append(pre_dict[data[0]])
        else:
            part = data[0].split(" ")
            instance = []
            instance.append(part[0])
            instance.append(part[1])
            length = len(part)

            for idx in xrange(2, length):
                tmp = part[idx].split(":")
                #if tmp[1] == "-1":
                #    continue
                instance.append(part[idx])
            new_ins = " ".join(instance)
            if len(new_ins) == 0:
                continue

            new = "\"" + new_ins + "\""
            cmd = "sh run.sh %s" %(new)
            p = os.popen(cmd)

            out = p.readline().strip()
            part = out.split("\t")
            if len(part) < 3:
                print >>sys.stderr, new_ins
                continue
            pre_dict[data[0]] = out
            to_print.append(out)

        length = len(data)
        for idx in xrange(1, length):
            to_print.append(data[idx])

        print "%s\t%s" %(data[1], "\t".join(to_print))

def reduce():
    for line in sys.stdin:
        if not line:
            continue
        data = line.strip().split("\t")
        to_print = []
        length = len(data)
        for idx in xrange(1, length):
            to_print.append(data[idx])
        out = "\t".join(to_print)
        if len(out) != 0:
            print "%s#A" %(out)
        #winfoid \t predict_value \t source(pc or wise) \t wmatch
        nout = data[9] + "\t" + data[3] + "\t" + data[5] + "\t" + data[17]
        if len(nout) != 0:
            print "%s#B" %(nout)

if __name__ == "__main__":
    if sys.argv[1] == "mapper":
        mapper()
    else:
        reduce()
