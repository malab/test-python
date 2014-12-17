from rdflib import Graph
from FuXi.Rete.RuleStore import SetupRuleStore

from FuXi.Rete.Util import generateTokenSet
from FuXi.Horn.HornRules import HornFromN3

rule_store, rule_graph, network = SetupRuleStore(makeNetwork=True)
closureDeltaGraph=Graph()
network.inferredFacts = closureDeltaGraph
network
# <Network: 0 rules, 0 nodes, 0 tokens in working memory, 0 inferred tokens>
for rule in HornFromN3('http://fuxi.googlecode.com/hg/test/sameAsTestRules.n3'): 
    network.buildNetworkFromClause(rule)
"""
... 
<TerminalNode (owl:sameAs(?y ?x) :- owl:sameAs(?x ?y)) (pass-thru): CommonVariables: [?y, ?x] (0 in left, 0 in right memories)>
<TerminalNode (?p(?y ?o) :- And( owl:sameAs(?x ?y) ?p(?x ?o) )) : CommonVariables: [?x] (0 in left, 0 in right memories)>
"""
network
"""
<Network: 2 rules, 4 nodes, 0 tokens in working memory, 0 inferred tokens>
"""
factGraph = Graph().parse('http://fuxi.googlecode.com/hg/test/sameAsTestFacts.n3',format='n3')
network.feedFactsToAdd(generateTokenSet(factGraph))
print (closureDeltaGraph.serialize(format='n3'))

@prefix (ns1: <http://example.org/> .

ns1:bar ns1:x "xxxx";
    = ns1:bar,
        ns1:foo .

ns1:foo ns1:y "yyyy";
    = ns1:foo 