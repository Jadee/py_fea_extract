
def ACparse (g, f, o, string_to_parse):
    current_state = 0;
    for i in xrange(0, len(string_to_parse)):
        transition = str(current_state) + "\t" + string_to_parse[i]
        while not g.has_key(transition):
            current_state = f[current_state];
            transition = str(current_state) + "\t" + string_to_parse[i];
        current_state = g[transition];
        if o.has_key(current_state) and len(o[current_state]) > 0:
            #print o[current_state][0] + "\t",
            return True;
    return False;
    

def ACFindMatch (g, f, o, string_to_parse):
    current_state = 0;
    for i in xrange(0, len(string_to_parse)):
        transition = str(current_state) + "\t" + string_to_parse[i]
        while not g.has_key(transition):
            current_state = f[current_state];
            transition = str(current_state) + "\t" + string_to_parse[i];
        current_state = g[transition];
        if o.has_key(current_state) and len(o[current_state]) > 0:
            return o[current_state][0],
    return None;
 
# for mutiple patterns, build ac automata
def buildAC (pList):
    g = {}
    f = {}
    o = {}
    
    newStateId = 1;
    
    ## construct goto table
    for pattern in pList:
        current_state = 0;
        for c in pattern:
            transition = str(current_state) + "\t" + c;
            if g.has_key(transition):
                current_state = g[transition];
            else:
                g[transition] = newStateId;
                newStateId += 1;
                current_state = g[transition];
                
        if not o.has_key(current_state):
            o[current_state] = [];
        
        o[current_state].append(pattern);
            
    for i in xrange(0, 256):
        c = chr(i);
        transition = str(0) + "\t" + c;
        if not g.has_key(transition):
            g[transition] = 0;
    ## goto table finished
    ## construct failure table
 
    q = [];

    for i in xrange(0, 256):
        c = chr(i);
        transition = str(0) + "\t" + c;
        if g.has_key(transition) and g[transition] != 0:
            next_state = g[transition];
            f[next_state] = 0;
            q.append(next_state);
            
    while len(q) > 0:
        current_state = q[0];
        del q[0];
        
        
        for i in xrange(0, 256):
            c = chr(i);
            transition = str(current_state) + "\t" + c;
            if g.has_key(transition):
                next_state = g[transition];
                q.append(next_state);

                v = f[current_state];
                while not g.has_key(str(v) + "\t" + c):
                    v = f[v];
                f[next_state] = g[str(v) + "\t" + c];

                if o.has_key(next_state):
                    o[next_state].extend(o.get(f[next_state], []));
                else:
                    o[next_state] = o.get(f[next_state], []); # maybe this should not happen
    
    ## failure table finished
    return (g, f, o)
 
#test = ['aaa', 'she', 'his', 'hers'];
#(g, f, o) = buildAC(test)
#ACparse(g, f, o, '')
