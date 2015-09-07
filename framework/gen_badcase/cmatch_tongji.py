import sys

show = {}
click = {}
price = {}

if len(sys.argv) < 2:
    sys.exit()

input = open(sys.argv[1], "r")
for line in input:
    if not line:
        continue
    line = line.strip()
    data = line.split("\t")
    
    cmatch = data[0]
    show[cmatch] = show.get(cmatch, 0) + int(data[1])
    click[cmatch] = click.get(cmatch, 0) + int(data[2])
    price[cmatch] = price.get(cmatch, 0) + int(data[3])

for cmatch in show:
    print "%s\t%s\t%s\t%s" %(cmatch, show[cmatch], click[cmatch], price[cmatch])
