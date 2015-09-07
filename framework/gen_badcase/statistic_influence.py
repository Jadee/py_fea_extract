import sys

def read_winfoid(winfoidlist):
    inputfile = open(winfoidlist, "r")
    winfo_dict = {}
    for line in inputfile:
        if not line:
            continue
        line = line.strip()
        data = line.split("\t")

        winfoid = data[0]
        winfo_dict[winfoid] = 1
    inputfile.close()
    return winfo_dict

# input format:
#   winfoid \t tag \t cmatch \t wmatch \t bidword \t show \t click \t price \t url
def mapper(winfoidlist):
    winfo_dict = read_winfoid(winfoidlist)
    showdict = {}
    clickdict = {}
    pricedict = {}
    for line in sys.stdin:
        if not line:
            continue
        line = line.strip()
        data = line.split("\t")
        
        winfoid = data[0]
        if winfo_dict.has_key(winfoid) == False:
            continue

        show = data[5]
        click = data[6]
        price = data[7]
        cmatch = data[2]
        showdict[cmatch] = showdict.get(cmatch, 0) + int(show)
        clickdict[cmatch] = clickdict.get(cmatch, 0) + int(click)
        pricedict[cmatch] = pricedict.get(cmatch, 0) + int(price)
    for key in showdict:
        print "%s\t%s\t%s\t%s" %(key, showdict[key], clickdict[key], pricedict[key])

def reduce(): 
    showdict = {}
    clickdict = {}
    pricedict = {}
    for line in sys.stdin:
        if not line:
            continue
        line = line.strip()
        data = line.split("\t")
        
        cmatch = data[0]
        showdict[cmatch] = showdict.get(cmatch, 0) + int(data[1])
        clickdict[cmatch] = clickdict.get(cmatch, 0) + int(data[2])
        pricedict[cmatch] = pricedict.get(cmatch, 0) + int(data[3])
    for key in showdict:
        print "%s\t%s\t%s\t%s" %(key, showdict[key], clickdict[key], pricedict[key])
        
if __name__ == "__main__":
    if sys.argv[1] == "mapper":
        mapper(sys.argv[2])
    else:
        reduce()
