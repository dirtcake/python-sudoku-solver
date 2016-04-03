#!/bin/python3
import sys

from copy import deepcopy, copy

def load(filename):
    puzzle = []
    with open(filename) as f:
        for line in f.read().splitlines():
            puzzle.append([int(i) for i in line.split(' ')])
    return puzzle


def print_puzzle(puzzle):
    lc = 0
    for line in puzzle:
        if lc % 3 == 0:
            print('+-----+-----+-----+')
        lc += 1
        line_str = ' '.join([str(i) for i in line])
        print('|{}|{}|{}|'.format(line_str[0:5], line_str[6:11], line_str[12:17]))
    print('+-----+-----+-----+')

def init_graph():
    graph = {}
    for i in range(9):
        for j in range(9):
            adj = []

            # row
            adj.extend([(i, b) for b in range(9) if b != j])
            # column
            adj.extend([(a, j) for a in range(9) if a != i])
            # block
            block_row = i // 3
            block_col = j // 3
            adj.extend([(block_row * 3 + a, block_col * 3 + b) for a in range(3) for b in range(3) if a != j and b != j]) # block
            graph[(i, j)] = adj
    return graph


def init_domain(puzzle, graph):
    domain = {}
    for i, line in enumerate(puzzle):
        for j, cell in enumerate(line):
            if cell == 0:
                domain[(i, j)] = set(range(1,10))
                for cell in [puzzle[adj[0]][adj[1]] for adj in graph[(i, j)]]:
                    domain[(i, j)].discard(cell)
            else:
                domain[(i, j)] = set()
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
    for line in puzzle:
        for cell in line:
            if cell == 0:
                return False
    return True


def _solve(puzzle, graph, domain, depth=0):
    most_constrained = most_constrained_cell(domain)
    if is_solved(puzzle):
        return puzzle

    if most_constrained is not None: # puzzle isn't solved but still has 0's
        sorted_domain = sorted(domain[most_constrained],
            key=lambda value: affected_domains(graph, domain, most_constrained, value))
        for value in sorted_domain:
            newpuzzle = []
            for line in puzzle:
                newpuzzle.append(list(line))
            newdomain = deepcopy(domain)

            newpuzzle[most_constrained[0]][most_constrained[1]] = value
            newdomain[most_constrained] = set()

            _propogate(graph, newdomain, most_constrained, value)
            # print_puzzle(newpuzzle)
            # print(most_constrained, value)
            # print(graph[(4,1)])
            # input()
            sol = _solve(newpuzzle, graph, newdomain, depth+1)
            if sol is not None:
                return sol

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

    print_puzzle(solve(puzzle))
