
import sys

pc_all_show = 0
pc_all_clk = 0
pc_all_price = 0
wise_all_show = 0
wise_all_clk = 0
wise_all_price = 0

def function():
    log_tongji_data = open("../join_resource/log_tongji_data", "r")
    global pc_all_show
    global pc_all_clk
    global pc_all_price 
    global wise_all_show
    global wise_all_clk
    global wise_all_price
    for line in log_tongji_data:
        if not line:
            continue;
        line = line.strip('\n')
        data = line.split("\t")
        if data[0] == "pc_log":
            pc_all_show += int(data[1])
            pc_all_clk += int(data[2])
            pc_all_price += int(data[3])
        elif data[0] == "wise_log":
            wise_all_show += int(data[1])
            wise_all_clk += int(data[2])
            wise_all_price += int(data[3])

function()

if __name__ == "__main__":
    
    pc_revenue_thre = float(sys.argv[1])
    wise_revenue_thre = float(sys.argv[2])
    winfo_num = float(sys.argv[3])

    date = sys.argv[5]

    print "\n%s\tsummary info:" %(date)
    print "    \t show       \t    clk        \t    price(yuan)"
    print "pc  \t %s   \t%s   \t%s" % (pc_all_show, pc_all_clk, float(pc_all_price) / float(100))
    print "wise\t %s   \t%s   \t%s" % (wise_all_show, wise_all_clk, float(wise_all_price) / float(100))
    print "\n"

    print "cmatch info:"
    print "    \t show   \t    clk   \t    price(yuan)"
    cnt = 6
    pc_zuoce = 0
    wise_shangfang = 0
    pc_cmatch =["201", "204", "225"]
    pc_effect_show = 0
    pc_effect_clk = 0
    pc_effect_price = 0
    wise_effect_show = 0
    wise_effect_clk = 0
    wise_effect_price = 0
    while cnt < len(sys.argv):
        print "%s \t   %s   \t%s   \t%s" %(sys.argv[cnt], sys.argv[cnt + 1], sys.argv[cnt + 2], float(sys.argv[cnt + 3]) / float(100))
        if sys.argv[cnt] == "204" or sys.argv[cnt] == "225":
            pc_zuoce += float(sys.argv[cnt + 3]) / float(100)
        if sys.argv[cnt] == "222" or sys.argv[cnt] == "223":
            wise_shangfang += float(sys.argv[cnt + 3]) / float(100)
        if sys.argv[cnt] in pc_cmatch:
            pc_effect_show += int(sys.argv[cnt + 1])
            pc_effect_clk += int(sys.argv[cnt + 2])
            pc_effect_price += float(sys.argv[cnt + 3])
        else:
            wise_effect_show += int(sys.argv[cnt + 1])
            wise_effect_clk += int(sys.argv[cnt + 2])
            wise_effect_price += float(sys.argv[cnt + 3])
        cnt += 4

    print "\n"
    if pc_all_show != 0:
        probe1 = float(pc_effect_show) / float(pc_all_show) * 100
    else:
        probe1 = 0.00
    if pc_all_clk != 0:
        probe2 = float(pc_effect_clk) / float(pc_all_clk) * 100
    else:
        probe2 = 0.00
    if pc_all_price != 0:
        probe3 = float(pc_effect_price) / float(pc_all_price) * 100
    else:
        probe3 = 0.00
    if wise_all_show != 0:
        probe4 = float(wise_effect_show) / float(wise_all_show) * 100
    else:
        probe4 = 0.00
    if wise_all_clk != 0:
        probe5 = float(wise_effect_clk) / float(wise_all_clk) * 100
    else:
        probe5 = 0.00
    if wise_all_price != 0:
        probe6 = float(wise_effect_price) / float(wise_all_price) * 100
    else:
        probe6 = 0.00

    print "\n%s\tbadcase info:" %(date)
    print "    \t show       \t    clk        \t    price(yuan)"
    print "pc  \t %s(%.2f%%) \t%s(%.2f%%) \t%s(%.2f%%)" % (pc_effect_show, probe1, pc_effect_clk, probe2, float(pc_effect_price) / float(100), probe3)
    print "wise\t %s(%.2f%%) \t%s(%.2f%%) \t%s(%.2f%%)" % (wise_effect_show, probe4, wise_effect_clk, probe5, float(wise_effect_price) / float(100), probe6)
    print "winfo_num: %s" %(winfo_num)

    print "\n"
    if pc_zuoce > pc_revenue_thre or wise_shangfang > wise_revenue_thre:
        print "the effects of pc_zuoce_revenue or wise_shangfang_revenue is too large\n"
        print "the new dict will be clean out"
        print "the pc_threshold is: %s" %(pc_revenue_thre)
        print "the wise_threshold is: %s"  %(wise_revenue_thre)
    else:
        print "everything is ok"
