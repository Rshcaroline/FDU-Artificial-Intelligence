# -*- coding: utf-8 -*-
"""
@author: ReneeYe
"""

from functools import reduce

class BayesNet:
    def __init__(self, node_specs=[]):
        self.nodes = []
        self.variables = []
        for node_spec in node_specs:
            self.add(node_spec)

    def add(self, node_spec):
        """Add a node to the net. Its parents must already be in the
        net, and its variable must not."""
        node = BayesNode(*node_spec)
        assert node.variable not in self.variables
        self.nodes.append(node)
        self.variables.append(node.variable)
        for parent in node.parents:
            self.variable_node(parent).children.append(node)

    def variable_node(self, var):
        for n in self.nodes:
            if n.variable == var:
                return n
        raise Exception("No such variable: %s" % var)

    def variable_values(self, vars):
        return [True, False]
    
    def __repr__(self):
        return 'BayesNet(%r)' % self.nodes


class BayesNode:
    """A conditional probability distribution for a boolean variable,
    P(X | parents). Part of a BayesNet."""

    def __init__(self, x, parents, cpt):
        
        if isinstance(parents, str):
            parents = parents.split()

        # We store the table always in the third form above.
        if isinstance(cpt, (float, int)):  # no parents, 0-tuple
            cpt = {(): cpt}
        elif isinstance(cpt, dict):
            # one parent, 1-tuple
            if cpt and isinstance(list(cpt.keys())[0], bool):
                cpt = dict(((v,), p) for v, p in list(cpt.items()))

        assert isinstance(cpt, dict)
        for vs, p in list(cpt.items()):
            assert 0 <= p <= 1

        self.variable = x
        self.parents = parents
        self.cpt = cpt
        self.children = []
        
    def p(self, value, event):
        assert isinstance(value, bool)
        ptrue = self.cpt[event_values(event, self.parents)]
        return (ptrue if value else 1 - ptrue)

    def __repr__(self):
        return repr((self.variable, ' '.join(self.parents)))

class ProbDist:
    def __init__(self, varname='?', freqs=None):
        """If freqs is given, it is a dictionary of value: frequency pairs,
        and the ProbDist then is normalized."""
        self.prob = {}
        self.varname = varname
        self.values = []
        if freqs:
            for (v, p) in list(freqs.items()):
                self[v] = p
            self.normalize()

    def __getitem__(self, val):
        "Given a value, return P(value)."
        try:
            return self.prob[val]
        except KeyError:
            return 0

    def __setitem__(self, val, p):
        "Set P(val) = p."
        if val not in self.values:
            self.values.append(val)
        self.prob[val] = p

    def normalize(self):
        """Make sure the probabilities of all values sum to 1.
        Returns the normalized distribution.
        Raises a ZeroDivisionError if the sum of the values is 0."""
        total = sum(self.prob.values())
        if not isclose(total, 1.0):
            for val in self.prob:
                self.prob[val] = self.prob[val] * 1.0 / total
                # self.prob[val] /= total
        return self

    def show_approx(self, numfmt='%.3g'):
        """Show the probabilities rounded and sorted by key, for the
        sake of portable doctests."""
        return ', '.join([('%s: ' + numfmt) % (v, p)
                          for (v, p) in sorted(self.prob.items())])

class Factor:
    def __init__(self, variables, cpt):
        self.variables = variables
        self.cpt = cpt

    def __getitem__(self, val):
        "Given a value, return P(value)."
        try:
            return self.cpt[val]
        except KeyError:
            return 0
        
    def pointwise_product(self, other):
        variables = list(set(self.variables) | set(other.variables))
        cpt = {event_values(e, variables): self.p(e) * other.p(e)
               for e in all_events(variables, {})}
        return Factor(variables, cpt)

    def sum_out(self, var):
        variables = [X for X in self.variables if X != var]
        cpt = {event_values(e, variables): sum(self.p(extend(e, var, val)) for val in [True,False])
               for e in all_events(variables, {})}
        return Factor(variables, cpt)

    def p(self, e):
        return self.cpt[event_values(e, self.variables)]
    
    def normalize(self):
        total = sum(self.cpt.values())
        if not isclose(total, 1.0):
            for val in self.cpt:
                self.cpt[val] = self.cpt[val] * 1.0 / total
                # self.cpt[val] /= total
        return self

def joint_probability(x_group, d):
    prob_enumeration = enumerate_all(bn.variables, d, bn)
    a2 = elimination_ask(x_group, {}, bn)
    TorF_group = tuple([d[i] for i in a2.variables])
    prob_elimination = a2[TorF_group]
    return prob_enumeration, prob_elimination

def conditional_probability(x_group, parent_vars, all_evidence, parent_evidence, children_TorF_tuple):
    if len(x_group) > 1:
        x_group_all = x_group + parent_vars
        joint_all, _ = joint_probability(x_group_all, all_evidence)        
        condition, _ = joint_probability(parent_vars, parent_evidence)
        prob_enumeration = joint_all * 1.0 / condition
        a2 = elimination_ask(x_group, parent_evidence, bn)
        prob_elimination = a2[event_values(all_evidence, x_group)]
            
    else:
        a1 = enumeration_ask(x_group[0], parent_evidence, bn)
        a2 = elimination_ask(x_group[0], parent_evidence, bn)
        prob_enumeration = a1[children_TorF_tuple]
        prob_elimination = a2[(children_TorF_tuple,)]
    return prob_enumeration, prob_elimination

def process_P_Query(query):
    for i in range(len(query)):
        if query[i] == '(':
            l = i
        if query[i] == ')':
            r = i
    content = query[l + 1:r]
    prob_enumeration = 0
    prob_elimination = 0
    if '|' not in content: # joint/ marginal distribution
        groups = content.split(', ')
        d = dict()
        x_group = []
        for group in groups:
            if '=' in group:
                x, y = group.split(' = ')
                TorF = processTF(y)
                d[x] = TorF
                x_group.append(x)
        prob_enumeration, prob_elimination = joint_probability(x_group, d)

    else:  # conditional distribution
        children,  parents = content.split(' | ')
        parent_evidence = dict()
        all_evidence = dict()
        x_group = []
        parent_vars = []
        if ',' in parents:
            parent_groups = parents.split(', ')
            for i in range(len(parent_groups)):
                if '=' in parent_groups[i]:
                    x, y = parent_groups[i].split(' = ')
                    parent_evidence[x] = processTF(y)
                    parent_vars.append(x)
        else:
            if '=' in parents:
                x, y  = parents.split(' = ')
                parent_evidence[x] = processTF(y)
                parent_vars.append(x)
                        
        if ',' in children:
            all_evidence = parent_evidence.copy()
            child_group = children.split(', ')
            children_TorF_tuple = []
            for i in range(len(child_group)):
                child = child_group[i]
                if '=' in child:
                    child, y = child.split(' = ')
                    x_group.append(child)
                    all_evidence[child] = processTF(y)
                    children_TorF_tuple.append(processTF(y))
        else:
            if '=' in children:
                child, y = children.split(' = ')
                children_TorF_tuple = processTF(y)
                x_group = [child]
        prob_enumeration, prob_elimination = conditional_probability(x_group, parent_vars, all_evidence, parent_evidence, children_TorF_tuple)

    return prob_enumeration, prob_elimination

def processTF(symbol):
    if symbol == "+":
        return True
    else:
        return False

def event_values(event, variables):
    if isinstance(event, tuple) and len(event) == len(variables):
        return event
    else:
        return tuple([event[var] for var in variables])

def extend(s, var, val):
    "Copy the substitution s and extend it by setting var to val; return copy."
    s2 = s.copy()
    s2[var] = val
    return s2

def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    "Return true if numbers a and b are close to each other."
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def enumeration_ask(X, e, bn):
    # assert X not in e
    Q = ProbDist(X)
    # YOUR_CODE_HERE (hint: only two lines, fig14.9)
    for xi in bn.variable_values(X):
        Q[xi] = enumerate_all(bn.variables, extend(e, X, xi), bn)
    return Q.normalize()
    # END_YOUR_CODE
	
def enumerate_all(variables, e, bn):
    if not variables:
        return 1.0
    Y, rest = variables[0], variables[1:]
    Ynode = bn.variable_node(Y)
    # YOUR_CODE_HERE (hint: an if-statement)
    if Y in e:
        return Ynode.p(e[Y], e) * enumerate_all(rest, e, bn)
    else:
        return sum(Ynode.p(y, e) * enumerate_all(rest, extend(e, Y, y), bn) for y in bn.variable_values(Y))
    # END_YOUR_CODE
    
def all_events(variables, e):
    if not variables:
        yield e
    else:
        X, rest = variables[0], variables[1:]
        for e1 in all_events(rest, e):
            for x in [True, False]:
                yield extend(e1, X, x)

def sum_out(var, factors):
    result, var_factors = [], []
    for f in factors:
        if var in f.variables:
            var_factors.append(f)
        else:
            result.append(f)
    result.append(pointwise_product(var_factors).sum_out(var))
    return result

def pointwise_product(factors):
    return reduce(lambda f, g: f.pointwise_product(g), factors)

def make_factor(var, e, bn):
    cpt = dict()
    node = bn.variable_node(var)
    variables = [X for X in [var] + node.parents if X not in e]
    for event in all_events(variables, e):
        cpt[event_values(event, variables)] = node.p(event[var], event)
    return Factor(variables, cpt)
    
def elimination_ask(X, e, bn, order=reversed):
    # YOUR_CODE_HERE (hint: you can use make_factor() and sum_out(), refer fig 14.11)
    factors = []
    for var in order(bn.variables):
        factors.append(make_factor(var, e, bn))
        if var not in X and var not in e:
            factors = sum_out(var, factors)
    return pointwise_product(factors).normalize()
    # END_YOUR_CODE

bn = BayesNet()
query = []
finish_add_query = 0

while True:
    try:
        line = input().strip()
        if line != '******' and finish_add_query == 0:
            query.append(line)
            continue
    
        if line == '******' and finish_add_query == 0:
            finish_add_query = 1
    
        if finish_add_query == 1:
            if '***' not in line:
                if '|' not in line:  # no parent node
                    node = line
                    p = input().strip()
                    prob = float(p)
                    bn.add((node, '', prob))
                else:  # parent node
                    cpt = dict()
                    node, parents = line.split(' | ')
                    line = input().strip()
                    every_parents = parents.split()
    
                    for i in range(int(2**len(every_parents))):
                        match = line.split()
                        if len(match) == 2:
                            match[1] = processTF(match[1])
                            cpt[match[1]] = float(match[0])
                        if len(match) == 3:
                            match[1] = processTF(match[1])
                            match[2] = processTF(match[2])
                            cpt[(match[1], match[2])] = float(match[0])
                        if len(match) == 4:
                            match[1] = processTF(match[1])
                            match[2] = processTF(match[2])
                            match[3] = processTF(match[3])
                            cpt[(match[1], match[2], match[3])] = float(match[0])
                        line = input().strip()
                    if not line:
                        bn.add((node, parents, cpt))
                    if line == '***' or line == '******':
                        bn.add((node, parents, cpt))
        if not line:
                break
            
    except EOFError:
        break


for i in query:
    prob_enumeration, prob_elimination = process_P_Query(i)
    print("probability by enumeration: ",round(prob_enumeration, 2))
    print("probability by elimination: ",round(prob_elimination, 2))
    print("**********")