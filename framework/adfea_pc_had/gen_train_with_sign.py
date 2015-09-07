#!/bin/env python
import sys


def read_fea_sign():
    dict = {}
    sign_file = open("fea_sign_dict.txt", "r")
    for line in sign_file:
        if not line:
            continue
        data = line.strip().split("\t")
        dict[data[0]] = data[1]
    return dict

def numeric_compare(fea1, fea2):
    part1 = fea1.split(":")
    part2 = fea2.split(":")
    return int(part1[0]) - int(part2[0])

def main():
    fea_sign_dict = read_fea_sign()

    for line in sys.stdin:
        if not line:
            continue
        line = line.strip()
        data = line.split("\t")
        extra = []
        length = len(data)
        for idx in xrange(1, length):
            extra.append(data[idx])

        part = data[0].split(" ")
        to_print = []
        length = len(part)
        for idx in xrange(2, length):
            tmp = part[idx].split(":")
            sign = fea_sign_dict[tmp[0]]
            value = "%s:%s" %(sign, tmp[1])
            to_print.append(value)
        out = sorted(to_print, numeric_compare)
        print "%s %s %s\t%s" %(part[0], part[1], " ".join(out), "\t".join(extra))

if __name__=="__main__":
    main()
