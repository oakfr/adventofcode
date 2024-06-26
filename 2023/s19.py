import re
import sys
import copy

def parse_part (line):
    d = re.match(r'{x=(\d+),m=(\d+),a=(\d+),s=(\d+)}', line)
    return [int(a) for a in [d.group(1), d.group(2), d.group(3), d.group(4)]]

def parse_rule (rules, line):
    d = re.match(r'(.+)\{(.+),(.+?)\}', line)
    r1 = d.group(1)
    r2 = d.group(2)
    r3 = d.group(3)
    xs = r2.split(',')
    rules[r1] = (xs, r3)
    # print(line)
    # print(f'{r1} --> {xs}\t\t{r3}')
    # print()

def sanity_check_rules (rules):
    allowed_keys = set(list(rules.keys()) + ['A', 'R'])
    for rule in rules.values():
        assert(rule[1] in allowed_keys)
        for x in rule[0]:
            assert(':' in x)
            assert('<' in x or '>' in x)


def read_lines (lines):
    rules = {}
    parts = []
    switch = False
    for line in lines:
        if not line:
            switch = True
            continue
        if switch:
            parts.append(parse_part(line))
        else:
            parse_rule(rules, line)
    return rules, parts

def run_rules (rules, parts):

    out = 0
    count = 0

    for p in parts:
        x = p[0]
        m = p[1]
        a = p[2]
        s = p[3]

        key = 'in'
        ans = None
        while True:
            rule = rules[key]
            key_changed = False
            for r in rule[0]:
                y = r.split(':')
                cond = y[0]
                outcome = y[1]
                if eval(cond):
                    key = outcome
                    #if key in ['A', 'R']:
                    #    ans = key
                    #    break
                    key_changed = True
                    break
            if not key_changed:
                key = rule[1]
            if key in ['A', 'R']:
                ans = key
                break

        assert (key in ['A', 'R'])
        if ans == 'A':
            out += sum(p)
            count += 1

    return out, count


filename = sys.argv[1]

with open(filename, 'r') as fh:
    lines = [a.strip() for a in fh.readlines()]
    rules, parts = read_lines (lines)

sanity_check_rules (rules)

#ans, count = run_rules (rules, parts)
#print(ans, count)


#########
# part 2

class Node:

    def __init__ (self, key, conds=None, parent=None):
        self.key = key
        self.parent = parent
        self.conds = conds
        self.children = []

    def __str__(self):
        parent_key = self.parent.key if self.parent else 'None'
        return f'[{self.key}] <- {parent_key}'

def not_cond (cond):
    if '>' in cond:
        return cond.replace('>', '<=')
    return cond.replace('<', '>=')

def rules_to_nodes (rules):
    """ convert rules into a graph and return the head (in) """
    head = Node('in')
    stack = [head]
    while stack:
        node = stack.pop()
        if node.key in ['A', 'R']:
            continue
        rule = rules[node.key]
        conditions = []
        for r in rule[0]:
            cond = r.split(':')[0]
            outcome = r.split(':')[1]
            c = Node(key=outcome, conds=' and '.join([not_cond(x) for x in conditions] + [cond]), parent=node)
            conditions.append(cond)
            node.children.append(c)
            stack.append(c)
        d = Node(key=rule[1], conds=' and '.join([not_cond(x) for x in conditions]), parent=node)
        stack.append(d)
        node.children.append(d)
    return head

def print_node (node):
    parent_key = node.parent.key if node.parent else 'None'
    print(f'# {node.key} <- {parent_key}')
    for c in node.children:
        print(f'\t > {c.key}')
    print()

    for c in node.children:
        print_node(c)

leafs = []

def leaf_nodes (node):
    """ list the leaf nodes in the graph (i.e. those ending with an Accept) """
    if node.key == 'A':
        leafs.append(node)
    for c in node.children:
        leaf_nodes(c)

def backtrack_node (node):
    ans = []
    conds = []
    while node:
        ans.append(node)
        conds.append(node.conds)
        node = node.parent
    return ans, conds

def new_range_with_max (range, mx):
    if mx < range[0]:
        return [0, -1]
    return [range[0], min(range[1], mx-1)]
        
def new_range_with_min (range, mn):
    if mn > range[1]:
        return [0, -1]
    return [max(range[0], mn+1), range[1]]

def conds_to_ranges (conds):
    """ convert conditions as strings into ranges of ints """
    vars = ['x', 'm', 'a', 's']
    MAXV = 4000
    ans = [[1,MAXV], [1,MAXV], [1,MAXV], [1,MAXV]]
    for cond in conds:
        g = re.match(r'(\w)<(\d+)', cond)
        if g:
            v = g.group(1)
            r = int(g.group(2))
            ind = vars.index(v)
            ans[ind] = new_range_with_max (ans[ind], r)
        g = re.match(r'(\w)>(\d+)', cond)
        if g:
            v = g.group(1)
            r = int(g.group(2))
            ind = vars.index(v)
            ans[ind] = new_range_with_min (ans[ind], r)
    return ans

def split_conds (conds):
    ans = []
    for c in conds:
        x = c.split(' and ')
        ans += x
    return ans

def are_valid_ranges (ranges):
    for c in ranges:
        if c[0] > c[1]:
            return False
    return True

def preprocess_cond (cond):
    g = re.match(r'(\w)<=(\d+)', cond)
    if g:
        v = g.group(1)
        r = int(g.group(2))
        return f'{v}<{r+1}'
    g = re.match(r'(\w)>=(\d+)', cond)
    if g:
        v = g.group(1)
        r = int(g.group(2))
        return f'{v}>{r-1}'
    return cond

def intersect_ranges (c1, c2):
    ans = copy.deepcopy(c1)
    for k in range(4):
        ans[k] = new_range_with_min(ans[k], c2[k][0]-1)
        ans[k] = new_range_with_max(ans[k], c2[k][1]+1)
    return ans

def range_surface (r):
    if not are_valid_ranges(r):
        return 0
    ans = 1
    for k in range(4):
        ans *= r[k][1] - r[k][0] + 1
    assert(ans > 0)
    return ans

def solve (rset):
    ans = sum([range_surface(x) for x in rset])
    n = len(rset)
    for i in range(n-1):
        for j in range(i+1, n):
            x = intersect_ranges(rset[i], rset[j])
            ans -= range_surface(x)
    return ans
                
# main code

head = rules_to_nodes (rules)

leaf_nodes(head)

range_set = []

for a in leafs:
    path, conds = backtrack_node(a)
    conds = conds[:-1]
    conds = list(map(lambda a: preprocess_cond(a), split_conds(conds)))
    ranges = conds_to_ranges(conds)
    if are_valid_ranges(ranges):
        range_set.append(ranges)

a = solve (range_set)
print(f'{a:_}') # expected 167409079868000
