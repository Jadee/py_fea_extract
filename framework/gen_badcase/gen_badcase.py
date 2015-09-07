# -*- coding: gbk -*-

import sys
import urllib
import ConfigParser

import acMatching

parse_field_index = {}
field_length = 0
user_bidword_pair_dict = {}
sex_term_dict = {}
famous_people_dict = {}
goals_sex_term = "NULL"
goals_famous_term = "NULL"
goals_lose_weight = "NULL"
lose_weight_dict = {}

video_whitelist_dict = {}
video_patterns = []

def get_field_index(fea_common_conf_filename):
    global field_length
    global parse_field_index
    config = ConfigParser.ConfigParser()
    config.readfp(open(fea_common_conf_filename, "r"))
    shitu_field = config.get("pre_out_fea_field", "schema")
    column = shitu_field.strip().split(",")
    field_length = len(column)
    for idx in xrange(0, field_length):
        parse_field_index[column[idx]] = idx

def filter_bidwordIsNumberOrEnglish(line):
    data = line.split("\t")
    bidword = data[parse_field_index["bidword"]]
    try:
        if len(unicode(bidword,'gb18030')) == len(bidword):
            return True
        else:
            return False
    except:
        return False

def read_user_bidword_trade():
    global user_bidword_pair_dict
    inputfile = open("user_bidword_trade.dict", "r")
    for line in inputfile:
        if not line:
            continue
        line = line.strip()
        if len(line) == 0:
            continue
        user_bidword_pair_dict[line] = 1
    inputfile.close()
    
def filter_user_bidword_trade(line):
    data = line.strip().split("\t")

    user_trade = data[parse_field_index["user_trade"]]
    bidword_trade = data[parse_field_index["bidword_trade"]]
    key = user_trade + " " + bidword_trade

    if user_bidword_pair_dict.has_key(key):      #²»ÊÇÂÒÂò´Ê
        return True
    else:
        return False
    
def read_sex_term():
    inputfile = open("sex_term_dict", "r")
    global sex_term_dict
    for line in inputfile:
        if not line:
            continue
        line = line.strip()
        data = line.split("\t")
        if len(data[0]) == 0:
            continue
        word = unicode(data[0], 'gb18030')
        sex_term_dict[word] = 1
    inputfile.close()
        
def filter_sex_term(line, threshold):
    global goals_sex_term
    data = line.strip().split("\t")
    
    pre_value = float(data[parse_field_index["pre_value"]])
    if pre_value > float(threshold):
        return False
        
    bidword = unicode(data[parse_field_index["bidword"]], 'gb18030')
    desc = unicode(data[parse_field_index["desc1"]], 'gb18030')
    title =  unicode(data[parse_field_index["title"]], 'gb18030')
    bidword_trade = data[parse_field_index["bidword_trade"]]
    flag_bidword = 0
    for term in sex_term_dict:
        if bidword.find(term) >= 0:    #±íÊ¾bidwordÖÐÓÐsex term
            flag_bidword = 1
            goals_sex_term = term.encode("gb18030")
            break

    if bidword_trade[0:4] == "5501" or bidword_trade == "820103" or bidword_trade == "820104":
        flag_bidword = 1
    
    flag_desc = 0
    for term in sex_term_dict:
        if desc.find(term) >= 0:       #±íÊ¾descÖÐÓÐsex term
            flag_desc = 1
            goals_sex_term = term.encode("gb18030")
            break

    flag_title = 0
    for term in sex_term_dict:
        if title.find(term) >= 0:
            flag_title = 1
            goals_sex_term = term.encode("gb18030")
            break
                
    if flag_bidword == 0 and flag_desc == 1:    #±íÊ¾ÊÇÂÒÂò´Ê
        return True

    if flag_bidword == 0 and flag_title == 1:
        return True
        
    return False

def read_lose_weight():
    inputfile = open("lose_weight_dict", "r") 
    global lose_weight_dict
    for line in inputfile:
        if not line:
            continue
        line = line.strip()
        data = line.split("\t")
        if len(data[0]) == 0:
            continue
        word = unicode(data[0], 'gb18030')
        lose_weight_dict[word] = 1
    
def filter_lose_weight(line, threshold):
    global goals_lose_weight
    data = line.strip().split("\t")
    
    pre_value = float(data[parse_field_index["pre_value"]])
    if pre_value > float(threshold):
        return False
        
    bidword = unicode(data[parse_field_index["bidword"]], 'gb18030')
    desc = unicode(data[parse_field_index["desc1"]], 'gb18030')
    title =  unicode(data[parse_field_index["title"]], 'gb18030')
    bidword_trade = data[parse_field_index["bidword_trade"]]
    flag_bidword = 0
    for term in lose_weight_dict:
        if bidword.find(term) >= 0:    #±íÊ¾bidwordÖÐÓÐsex term
            flag_bidword = 1
            break
    if bidword_trade[0:4] == "8203" or bidword_trade == "820802":
        flag_bidword = 1

    flag_desc = 0
    for term in lose_weight_dict:
        if desc.find(term) >= 0:       #±íÊ¾descÖÐÓÐsex term
            flag_desc = 1
            goals_lose_weight = term.encode("gb18030")
            break
    
    flag_title = 0
    for term in lose_weight_dict:
        if title.find(term) >= 0:
            flag_title = 1
            goals_lose_weight = term.encode("gb18030")
            break
                
    if flag_bidword == 0 and flag_desc == 1:    #±íÊ¾ÊÇÂÒÂò´Ê
        return True

    if flag_bidword == 0 and flag_title == 1:
        return True

    return False
        
        
def read_famous_people_dict():
    global famous_people_dict
    inputfile = open("famous_people_dict", "r")
    for line in inputfile:
        if not line:
            continue
        line = line.strip()
        if len(line) == 0:
            continue
        line = unicode(line, 'gb18030')
        famous_people_dict[line] = 1
    inputfile.close()

def filter_famous_people(line, threshold):
    global goals_famous_term
    data = line.strip().split("\t")
    pre_value = float(data[parse_field_index["pre_value"]])

    if pre_value > float(threshold):
        return False

    bidword = data[parse_field_index["bidword"]]
    bidword = unicode(bidword, 'gb18030')

    for name in famous_people_dict:
        if bidword.find(name) >= 0:
            goals_famous_term = name.encode("gb18030")
            return True
            break
    return False
    

def filter_high_clickq(line, pc_wildword_upper_threshold, wise_wildword_upper_threshold, \
        app_wildword_upper_threshold, pc_wildword_lower_threshold, \
        wise_wildword_lower_threshold, app_wildword_lower_threshold, clickq_threshold):
    
    data = line.strip().split("\t")
    pre_value = float(data[parse_field_index["pre_value"]])
    click_q = float(data[parse_field_index["non_per_click_q"]])
    source = data[parse_field_index["source"]]
    mt_id = data[parse_field_index["mt_id"]]

    if source == "pc":
        if pre_value < float(pc_wildword_upper_threshold) \
            and pre_value >= float(pc_wildword_lower_threshold) \
            and click_q < float(clickq_threshold):
            return True
        else:
            return False
    elif source == "wise":
        if mt_id.find("2002") >= 0:     #wise app ads
            if pre_value < float(app_wildword_upper_threshold) \
                and pre_value >= float(app_wildword_lower_threshold) \
                and click_q < float(clickq_threshold):
                return True
            else:
                return False
        else:
            if pre_value < float(wise_wildword_upper_threshold) \
                and pre_value >= float(wise_wildword_lower_threshold) \
                and click_q < float(clickq_threshold):
                return True
            else:
                return False
    else:
        return False

def filter_badcase(line, pc_wildword_threshold, wise_wildword_threshold, app_wildword_threshold):
    data = line.strip().split("\t")
    pre_value = float(data[parse_field_index["pre_value"]])

    source = data[parse_field_index["source"]]
    mt_id = data[parse_field_index["mt_id"]]

    if source == "pc":
        if pre_value < float(pc_wildword_threshold):
            return True
        else:
            return False
    elif source == "wise":
        if mt_id.find("2002") >= 0:     #wise app ads
            if pre_value < float(app_wildword_threshold):
                return True
            else:
                return False
        else:
            if pre_value < float(wise_wildword_threshold):
                return True
            else:
                return False
    else:
        return False


def read_video_whitelist():
    global video_whitelist_dict
    inputfile = open("video_whitelist.txt", "r")
    for line in inputfile:
        if not line:
            continue
        line = line.strip()
        video_whitelist_dict[line] = 1
    inputfile.close()

def read_video_patterns():
    read_video_whitelist()
    global video_patterns
    inputfile = open("video_dict.txt", "r")
    for line in inputfile:
        if not line:
            continue
        data = line.strip().split("\t")
        if len(data[0]) > 4 and not video_whitelist_dict.has_key(data[0]):
            video_patterns.append(data[0])

def filter_video_badcase(line, video_badcase_thre, video_clickq_thre, goToFun, failed, output):
    data = line.strip().split("\t")
    user_trade = data[parse_field_index["user_trade"]]
    bidword_trade = data[parse_field_index["bidword_trade"]]
    clickq = float(data[parse_field_index["non_per_click_q"]])
    pre_value = float(data[parse_field_index["pre_value"]])
    bidword = data[parse_field_index["bidword"]]

    if user_trade[0:2] != bidword_trade[0:2] and pre_value < float(video_badcase_thre) \
        and clickq < float(video_clickq_thre) and acMatching.ACparse(goToFun, failed, output, bidword):
            
        if len(user_trade) >= 2 and user_trade[0:2] != "83" and user_trade[0:2] != "75" and user_trade[0:2] != "60" \
            and user_trade[0:2] != "54" and user_trade[0:2] != "79" and user_trade[0:2] != "71":
            return True

    return False

def filter_low_clickq(line, clickq_low_thre, badcase_low_thre):
    clickq = float(data[parse_field_index["non_per_click_q"]])
    pre_value = float(data[parse_field_index["pre_value"]])

    if clickq < float(clickq_low_thre) and pre_value < float(badcase_low_thre):
        return True
    else:
        return False
    
if __name__ == "__main__":
    field_conf_filename = sys.argv[1]
    threshold_conf_filename = sys.argv[2]
    
    config = ConfigParser.ConfigParser()
    config.readfp(open(threshold_conf_filename, "r"))

    #*******************read gflags********************************************
    
    gflags_china_char_rule = int(config.get("rule_gflags", "gflags_china_char_rule"))
    gflags_trade_rule = int(config.get("rule_gflags", "gflags_trade_rule"))
    gflags_sex_rule = int(config.get("rule_gflags", "gflags_sex_rule"))
    gflags_video_rule = int(config.get("rule_gflags", "gflags_video_rule"))
    gflags_famous_people_rule = int(config.get("rule_gflags", "gflags_famous_people_rule"))
    gflags_lose_weight_rule = int(config.get("rule_gflags", "gflags_lose_weight_rule"))
    gflags_high_clickq_rule = int(config.get("rule_gflags", "gflags_high_clickq_rule"))
    gflags_low_clickq_rule = int(config.get("rule_gflags", "gflags_low_clickq_rule"))
    gflags_badcase_rule = int(config.get("rule_gflags", "gflags_badcase_rule"))
    
    #**************************************************************************
   
    #***********read threshold*************************************************
    sex_term_threshold = float(config.get("sex_term_threshold", "sex_rule_value"))
    famous_people_threshold = float(config.get("famous_people_threshold", "famous_rule_value"))
    lose_weight_threshold = float(config.get("lose_weight_threshold", "lose_weight_value"))

    video_badcase_thre = float(config.get("video_rule_threshold", "video_badcase_value"))
    video_clickq_thre = float(config.get("video_rule_threshold", "video_clickq_value"))

    low_clickq_thre = float(config.get("filter_low_clickq", "low_clickq_threshold"))
    low_wildword_thre = float(config.get("filter_low_clickq", "low_wildword_threshold"))
    
    pc_wildword_upper_threshold = float(config.get("filter_high_clickq", "pc_wildword_upper_threshold"))
    wise_wildword_upper_threshold = float(config.get("filter_high_clickq", "wise_wildword_upper_threshold"))
    app_wildword_upper_threshold = float(config.get("filter_high_clickq", "app_wildword_upper_threshold")) 
    pc_wildword_lower_threshold = float(config.get("filter_high_clickq", "pc_wildword_lower_threshold"))
    wise_wildword_lower_threshold = float(config.get("filter_high_clickq", "wise_wildword_lower_threshold"))
    app_wildword_lower_threshold = float(config.get("filter_high_clickq", "app_wildword_lower_threshold"))
    clickq_threshold = float(config.get("filter_high_clickq", "clickq_threshold"))
    
    pc_wildword_threshold = float(config.get("badcase_threshold", "pc_wildword_threshold"))
    wise_wildword_threshold = float(config.get("badcase_threshold", "wise_wildword_threshold"))
    app_wildword_threshold = float(config.get("badcase_threshold", "app_wildword_threshold"))
    #**************************************************************************
    
    #***********prepare work***************************************************
    get_field_index(field_conf_filename)
    read_user_bidword_trade()
    read_sex_term()
    read_famous_people_dict()
    read_lose_weight()
    read_video_patterns()

    (goToFun, failed, output) = acMatching.buildAC(video_patterns);
    #**************************************************************************    
    
    for line in sys.stdin:
        if not line:
            continue
        line = line.strip()
        data = line.split("\t")
        if len(data) != field_length:
            continue
        
        if gflags_china_char_rule == 1 and filter_bidwordIsNumberOrEnglish(line) == True:    #±íÊ¾bidword ÊÇÓ¢ÎÄ»òÊý×Ö
            continue

        if gflags_trade_rule == 1 and filter_user_bidword_trade(line) == True:
            continue

        if gflags_sex_rule == 1 and filter_sex_term(line, sex_term_threshold) == True:  #ÊÇÂÒÂò´Ê ¾ÍÊä³ö
            print "sex_term_%s\t%s"  %(goals_sex_term, line)
            continue

        if gflags_famous_people_rule == 1 and filter_famous_people(line, famous_people_threshold) == True:  #ÊÇÂÒÂò´Ê ¾ÍÊä³ö
            print "famous_term_%s\t%s"  %(goals_famous_term, line)
            continue

        if gflags_lose_weight_rule == 1 and filter_lose_weight(line, lose_weight_threshold) == True:
            print "lose_weight_%s\t%s"  %(goals_lose_weight, line)
            continue 

        if gflags_video_rule == 1 and filter_video_badcase(line, video_badcase_thre, video_clickq_thre, goToFun, failed, output) == True:
            print "video_rule\t%s"  %(line)
            continue

        if gflags_high_clickq_rule == 1 and filter_high_clickq(line, pc_wildword_upper_threshold, wise_wildword_upper_threshold, \
                app_wildword_upper_threshold, pc_wildword_lower_threshold, wise_wildword_lower_threshold, \
                app_wildword_lower_threshold, clickq_threshold) == True:
            print "high_clickq\t%s"  %(line)
            continue

        if gflags_badcase_rule == 1 and filter_badcase(line, pc_wildword_threshold, wise_wildword_threshold, app_wildword_threshold) == True:
            print "badcase\t%s"  %(line)
            continue

        if gflags_lose_weight_rule == 1 and filter_low_clickq(line, low_clickq_thre, low_wildword_thre) == True:
            print "low_clickq\t%s"  %(line)
            continue
