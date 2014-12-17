#
#   s i r . p y
#  http://www.openbookproject.net/py4fun/sir/sir.html
import re, sys

debug = 0
facts = []
"""
"s" is subset, "S" is superset
"m" is member, "M" is contains
"e" is equivalent
"p" is "possess", "P" is "possessed by"
"""
rules = (
 ( "(todo|toda|todos|todas|cualquier|uno|una|unos|unas) (.*) (es|son|^no es|^no son) (un|una|unos|unas) (.*)",   lambda g: addFact(g,"1s4|4S1")),
 ( "(.*) (es|son|^no es|^no son) (un|una|unos|unas) (.*)",                    lambda g: addFact(g,"0m3|3M0")),
 ( "(.*) (es|son|^no es|^no son) (.*)",                           lambda g: addFact(g,"0e2|2e0")),
 
 ( "(todo|toda|todos|todas|cualquier|uno|una|unos|unas) (.*) (posee|poseen|tiene|tienen) (un|una|unos|unas) (.*)", lambda g: addFact(g,"1p4|4P1")),
 ( "(.*) (posee|poseen|tiene|tienen|^no posee|^no poseen|^no tiene|^no tienen) (un|una|unos|unas) (.*)",                  lambda g: addFact(g,"0p3|3P0")),
 ( "(.*) (posee|poseen|tiene|tienen|^no posee|^no poseen|^no tiene|^no tienen) (.*)",                         lambda g: addFact(g,"0p2|2P0")),
 
 ( "is (every|an|a) (.*) (a|an) (.*)",       lambda g: getPath(g,"1e*s*3")),
 ( "is (.*) (a|an) (.*)",                    lambda g: getPath(g,"0e*ms*2")),
 ( "does (every|an|a) (.*) own (a|an) (.*)", lambda g: getPath(g,"1e*ms*ps*3")),
 ( "does any (.*) own (a|an) (.*)",          lambda g: getPath(g,"0S*Me*ps*2")),
 ( "does (.*) own (a|an) (.*)",              lambda g: getPath(g,"0e*ms*ps*2")),
 ( "dump",                                   lambda g: dump()              ),
 ( "debug",                                  lambda g: toggleDebug()       ),
 ( "quit",                                   lambda g: sys.exit()          ),
)

def addFact(grp, phrases) :
    global facts
    for p in phrases.split("|") :
        f = (grp[int(p[0])], p[1], grp[int(p[2])])
        if debug : print(("  adding fact", f))
        facts.append(f)
    print ("  I understand")

def matchSent (sent) :
    sent = re.sub("  *"," ",sent.strip().lower())
    for pattern, action in rules :
        match = re.match(pattern, sent)
        if match :
            action(match.groups())
            # print("*"*20, "\n", match.groups())
            return
            
def getPath (grp, rule) :
    pattern = rule[1:-1]; start=grp[int(rule[0])]; stop=grp[int(rule[-1])]
    ans = []
    p = path(pattern, start, stop, ans=ans)
    if debug : detail = "%s %s" % (pattern,ans)
    else     : detail = ""
    if ans : print(("  Yes", detail))
    else   : print(("  Not sure", detail))

def path (pat, start, end, before={}, ans=[], sofar="", indent=" ") :
    used = {}
    used.update(before)
    if debug : print((indent,"path - ",start," to ",end))
    if len(indent) > 20 : return
    for fact in facts :
        if used.get(fact) : continue
        a,rel,b = fact
        if  a != start : continue
        sts = okSoFar(pat, sofar+rel)
        if not sts : continue
        used[fact] = 1
        if b == end :
            if sts == 2 : ans.append(sofar+rel)
        else :
            # find inner solutions recursively
            path (pat, b, end, used, ans, sofar+rel, indent+"  ")

def okSoFar (a, b) :
    "return 1 for partial match, 2 for complete match"
    ans = 2
    while a :
        if re.match("^%s$"%a, b) : return ans
        if a[-1] == '*' : a = a[:-2]
        else            : a = a[:-1]
        ans = 1
    return 0

def toggleDebug () :
    global debug
    debug = not debug

def dump () :
    for p,rel,q in facts : print(("  %-10s : %s : %s" % (p,rel,q)))

def main () :
    sys.stderr = sys.stdout
    #files = ['data/white-ship.txt']
    files = ['data/durruti.txt']
    #for file in sys.argv[1:] :
    toggleDebug()
    for file in files:
        if file == '.' : return
        lins = open(file).readlines()
        for lin in lins :
            # print (lin.strip())
            matchSent (lin)
    # dump()
    while 1 :
        sent = eval(input("? "))
        matchSent(sent)
    
    
        
if __name__ == "__main__" : main()