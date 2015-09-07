# -*- coding: gbk -*-
import sys
import string
import re

delEStr = string.maketrans(string.punctuation, " " * len(string.punctuation))
delCStr = ["，", "。", "（", "）", "：", "；", "《", "》", "！", "【", "】", "’", "”", "、", "？", "·"]

def handle_str(SrcStr):
    for sign in delCStr:
        SrcStr = SrcStr.replace(sign, " ")
    SrcStr = SrcStr.translate(delEStr)
    SrcStr = re.sub(r'\s+', ' ', SrcStr).strip()
    SrcStr = SrcStr.replace(" ", ",")
    return SrcStr
'''
if __name__ == "__main__":
    print handle_str("a d !c")
'''
