import sys


index = 1
for line in sys.stdin:
    if not line:
        continue
    data = line.strip().split(";")

    if len(data) < 1:
        continue

    part = data[0].split("=")
    if len(part) < 2:
        continue
    if part[0] == "name":
        print "%s\t%s" %(part[1], index)
        index += 1
