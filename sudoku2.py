#!/bin/python3
import sys

from copy import deepcopy, copy

def load(filename):
    puzzle = []
    with open(filename) as f:
        for line in f.read().splitlines():
            puzzle.extend([int(i) for i in line.split(' ')])
    return puzzle


def print_puzzle(puzzle):
    lc = 0
    for i in range(9):
        if lc % 3 == 0:
            print('+-----+-----+-----+')
        lc += 1
        line_str = ' '.join([str(i) for i in puzzle[i*9:i*9+9]])
        print('|{}|{}|{}|'.format(line_str[0:5], line_str[6:11], line_str[12:17]))
    print('+-----+-----+-----+')


def init_graph():
    graph = {}
    for i in range(9):
        for j in range(9):
            adj = []

            # row
            adj.extend([i*9 + b for b in range(9) if b != j])
            # column
            adj.extend([a*9 + j for a in range(9) if a != i])
            # block
            block_row = i // 3
            block_col = j // 3
            adj.extend([(block_row * 3 + a) * 9 + (block_col * 3 + b) for a in range(3) for b in range(3) if a != j and b != j]) # block
            graph[i*9 + j] = adj
    return graph


def init_domain(puzzle, graph):
    domain = {}
    for i, cell in enumerate(puzzle):
        if cell == 0:
            domain[i] = set(range(1,10))
            for cell in [puzzle[adj] for adj in graph[i]]:
                domain[i].discard(cell)
        else:
            domain[i] = set()
    print(domain)
    return domain


def most_constrained_cell(domain):
    min_size = 2147483647
    most_constrained = None
    for pos, dom in domain.items():
        if len(dom) < min_size and len(dom) != 0:
            min_size = len(dom)
            most_constrained = pos
    return most_constrained


def affected_domains(graph, domain, pos, value):
    '''returns number of adjacent domains of 'pos' that 'value' constrains'''

    least_affected = 2147483647
    count = 0
    for cell in graph[pos]:
        if value in domain[cell]:
            count += 1
    return count


def _propogate(graph, domain, pos, value):
    for cell in graph[pos]:
        if len(domain[cell]) != 0: # len == 0 means this cell is filled
            domain[cell].discard(value)


def is_solved(puzzle):
    return 0 not in puzzle


def _solve(puzzle, graph, domain, depth=0):
    most_constrained = most_constrained_cell(domain)
    if is_solved(puzzle):
        return puzzle

    if most_constrained is not None: # puzzle isn't solved but still has 0's
        # sort domain by least constraining value
        sorted_domain = sorted(domain[most_constrained],
            key=lambda value: affected_domains(graph, domain, most_constrained, value))

        # save current domain
        old_domain = {}
        for pos in graph[most_constrained]:
            old_domain[pos] = deepcopy(domain[pos])
        old_domain[most_constrained] = deepcopy(domain[most_constrained])

        for value in sorted_domain:
            newpuzzle = list(puzzle)

            newpuzzle[most_constrained] = value
            domain[most_constrained] = set()

            _propogate(graph, domain, most_constrained, value)

            sol = _solve(newpuzzle, graph, domain, depth+1)
            if sol is not None:
                return sol

            # restore domain
            for pos in graph[most_constrained]:
                domain[pos] = deepcopy(old_domain[pos])
            domain[most_constrained] = deepcopy(old_domain[most_constrained])


def solve(puzzle):
    graph = init_graph()
    domain = init_domain(puzzle, graph)
    return _solve(puzzle, graph, domain)


if __name__ == '__main__':

    if len(sys.argv) == 1:
        filename = 'hw1.txt'
    else:
        filename = sys.argv[1]
    puzzle = load(filename)
    print_puzzle(puzzle)

    print_puzzle(solve(puzzle))
