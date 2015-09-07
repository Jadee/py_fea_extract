import os;
import sys;

chunk = int(sys.argv[1]);

prev_key = "";
prev_vec = chunk * [0];
cnt = 0;

# input:
#   1. url \t vec1 \t freq1
#   2. url \t vec2 \t freq2
# output:
#   1. url \t tag(1) \t vector
for line in sys.stdin:
    if not line:
        continue;
    
    data = line.strip('\n').split('\t');
    key = data[0];
    vec_string = data[1];
    freq = float(data[2]);
    
    vec = vec_string.split(' ');
    
    if key == prev_key:
        cnt = cnt + freq;
        prev_vec = [x + float(y)*freq for x,y in zip(prev_vec, vec)];
    else:
        if prev_key == "":
            pass;
        else:
            prev_vec = [x / cnt for x in prev_vec];
            print prev_key + "\t1\t" + " ".join(map(str,prev_vec));
            
        prev_vec = map(float, vec);
        prev_key = key;
        cnt = freq;

# for the last record
if prev_key == "":
    pass;
else:
    prev_vec = [x / cnt for x in prev_vec];
    print prev_key + "\t1\t" + " ".join(map(str,prev_vec));
    
#prev_vec = map(float, vec);
#prev_key = key;

