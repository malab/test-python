from rdflib import Variable, Namespace
from rdflib import Graph
from FuXi.Rete.RuleStore import SetupRuleStore
from FuXi.Rete.Util import generateTokenSet
from FuXi.Horn.HornRules import HornFromN3
from FuXi.Rete.Magic import MagicSetTransformation, AdornLiteral
from FuXi.SPARQL import RDFTuplesToSPARQL

exNs = Namespace('http://dev.w3.org/2000/10/swap/test/cwm/fam.n3#')

rules = HornFromN3('http://dev.w3.org/2000/10/swap/test/cwm/fam-rules.n3')
factGraph = Graph().parse('http://dev.w3.org/2000/10/swap/test/cwm/fam.n3',format='n3')
factGraph.bind(u'ex',exNs)
dPreds = [exNs.ancestor]

rule_store, rule_graph, network = SetupRuleStore(makeNetwork=True)
network.nsMap = {u'ex':exNs}
closureDeltaGraph=Graph()
network.inferredFacts = closureDeltaGraph

goals = [(exNs.david,exNs.ancestor,Variable('ANCESTOR'))]
for rule in MagicSetTransformation(factGraph,rules,goals,dPreds):
    network.buildNetworkFromClause(rule)    
    # network.rules.add(rule)
    print ("\t", rule)
    
goalLit = AdornLiteral(goals[0])
adornedGoalSeed = goalLit.makeMagicPred()
goal=adornedGoalSeed.toRDFTuple()
print (RDFTuplesToSPARQL([goalLit],factGraph,vars=[Variable('ANCESTOR')])
SELECT ?ANCESTOR {      <http://dev.w3.org/2000/10/swap/test/cwm/fam.n3#david> <http://dev.w3.org/2000/10/swap/test/cwm/fam.n3#ancestor> ?ANCESTOR })
                  
                  