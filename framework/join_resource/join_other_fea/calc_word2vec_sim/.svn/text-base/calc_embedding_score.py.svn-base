# -*- coding: gbk -*-

import sys

# mapper input: 
#   1.winfoid \t term \t vector \t term_info
#   2.winfoid \t url  \t vector \t url_info
def mapper():
    for line in sys.stdin:
        if not line:
            continue
        data = line.strip().split("\t")
        print "%s\t%s\t%s" %(data[0], data[2], data[3])

# reduce output:
#   1.winfoid \t score
def reduce(VECTOR_SIZE):
    BIAS = 0.05;
    pre_key = ""
    query_vector = VECTOR_SIZE * [0];
    url_vector = VECTOR_SIZE * [0];

    for line in sys.stdin:
        if not line:
            continue
        data = line.strip().split("\t");
        if len(data) != 3:
            continue

        key = data[0]
        vector_str = data[1]
        value_name = data[2]

        if key != pre_key and pre_key != "":
            score = sum([x * float(y) for x,y in zip(query_vector, url_vector)]);
            print "%s\t%f" %(pre_key, score)

            query_vector = VECTOR_SIZE * [0];
            url_vector = VECTOR_SIZE * [0];

        if value_name == "term_info":
            term_vector = vector_str.split(" ");
            if len(term_vector) == VECTOR_SIZE:
                if key != pre_key:
                    query_vector = map(float, term_vector);
                else:
                    query_vector = [x + float(y) for x,y in zip(query_vector, term_vector)];
        elif value_name == "url_info":
            temp_vector = vector_str.split(" ");
            if len(temp_vector) == VECTOR_SIZE:
                if key != pre_key:
                    url_vector = map(float, temp_vector);
                else:
                    url_vector = [x + float(y) for x,y in zip(url_vector, temp_vector)];
        else:
            continue

        pre_key = key

    score = sum([x * float(y) for x,y in zip(query_vector, url_vector)]);
    print "%s\t%f" %(pre_key, score)

if __name__ == "__main__":
    if sys.argv[1] == "mapper":
        mapper()
    else:
        reduce(int(sys.argv[2]))
