import sys

def core_terms_1_parser(json_list):
    try:
        tmp = [];
        for element in json_list:
            trans = (element['term']) + ":" + str(element['weight']);
            tmp.append(trans);

        if len(tmp) == 0:
            return "\N"
        else:
            return ",".join(tmp);
    except Exception, e:
        return None;

def trade_parser(json_list):
    try:
        tmp = [];
        for element in json_list:
            trans = str(element['tradeid']) + ":" + str(element['weight']);
            tmp.append(trans);
        if len(tmp) == 0:
            return "\N"
        else:
            return ",".join(tmp);
    except Exception, e:
        return None;

fea_parser_dict = {'core_terms_1':core_terms_1_parser, \
                    'trade':trade_parser};
