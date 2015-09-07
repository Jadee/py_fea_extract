# -*- coding:utf-8 -*-
import sys
import string
import re

src = string.punctuation + ' '
delEStr = string.maketrans(src, " " * len(src))

def handle_str(SrcStr):
    SrcStr = SrcStr.replace("\t", " ").replace("\n", " ")
    SrcStr = SrcStr.translate(delEStr).strip().replace(" ", ",")
    SrcStr = re.sub(r',+', ',', SrcStr).strip()
    return SrcStr

'''
if __name__ == "__main__":
    print handle_str("�����ݵ��Ϻ���Ʊ�����ݵ��Ϻ��ؼۻ�Ʊ - ��Ѷ��Ʊ")
    for line in sys.stdin:
        if not line:
            break
        data = line.strip().split("\t")
        print handle_str(data[0])
'''
