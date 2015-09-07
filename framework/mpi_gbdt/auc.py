import sys

def auc( l ):
    total_score = 0
    pos = 0
    neg = 0
    score = len(l)
    for item in l:
        ptr = item[0]
        label = item[1]
        if label == 1:
            pos += 1
            total_score += score
            score -= 1
        elif label <= 0:
            neg += 1
            score -= 1

    pro = float(pos) * float(pos + 1) / float(2)
    return float(total_score - pro) / float(pos * neg)

def get_precision_recall(l, threshold):
    true_all = 0
    pos_all = 0
    true_pos = 0
    false_neg = 0
    neg_all = 0

    false_all = 0
    true_neg = 0
    false_pos = 0

    for item in l:
        ptr = float(item[0])
        label = int(item[1])
        if label > 0:
            true_all += 1
            if ptr > float(threshold):
                true_pos += 1
                pos_all += 1
            else:
                false_neg += 1
                neg_all += 1
        else:
            false_all += 1
            if ptr <= float(threshold):
                true_neg += 1
                neg_all += 1
            else:
                false_pos += 1
                pos_all += 1
    tp = float(true_pos)/float(pos_all)
    tr = float(true_pos)/float(true_all)
    fp = float(true_neg)/float(neg_all)
    fr = float(true_neg)/float(false_all)
    tf1 = 2*tp*tr / (tp+tr)
    ff1 = 2*fp*fr / (fp+fr)

    print "positive:%s\t%s\t%s" % (true_all, true_pos, pos_all)
    print "negative:%s\t%s\t%s" % (false_all, true_neg, neg_all)

    print "true precision:\t%f"%(tp)
    print "true recall:\t%f"%(tr)
    print "true F1:\t%f"%(tf1)
    print "flase precision:\t%f"%(fp)
    print "flase recall:\t%f"%(fr)
    print "flase F1:\t%f"%(ff1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        threshold = 0.5
    else:
        threshold = float(sys.argv[1])
    rec = []
    pos = 0
    neg = 0
    for line in sys.stdin:
        if not line:
            break

        data = line.strip().split('\t')
        ptr = float(data[3])
        label = float(data[2])
        if label == 1:
            pos += 1
        elif label == -1:
            neg += 1
        rec.append((ptr, label))

    print len(rec), threshold
    rec.sort(lambda x,y: cmp(y[0], x[0]))
    
    print 'auc :', auc(rec)
    get_precision_recall(rec, threshold)
