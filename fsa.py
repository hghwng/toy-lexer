#!/usr/bin/env python3
from copy import deepcopy


class Edge:
    def __init__(self, dst, val):
        self.val = val
        self.dst = dst


class State:
    def __init__(self):
        self.edges = list()


class FSA:
    def __init__(self):
        self.finals = list()
        self.states = [State()]

    def add_final(self, index):
        self.finals.append(index)

    def add_state(self) -> int:
        self.states.append(State())
        return len(self.states) - 1

    def add_final_state(self) -> int:
        state = self.add_state()
        self.add_final(state)
        return state

    def add_edge(self, src, dst, val):
        self.states[src].edges.append(Edge(dst, val))

    def add_edge_epsilon(self, src, dst):
        self.add_edge(src, dst, 0)

    def combine(self, fsa) -> int:
        offset = len(self.states)
        tmpfsa = fsa.duplicate()
        for state in tmpfsa.states:
            for edge in state.edges:
                edge.dst += offset
        for idx in range(len(tmpfsa.finals)):
            tmpfsa.finals[idx] += offset
        self.states.extend(tmpfsa.states)
        self.finals.extend(tmpfsa.finals)
        return offset

    def duplicate(self):
        return deepcopy(self)

    def dump(self, f):
        f.write('digraph {\n')
        for final in self.finals:
            f.write('\t' + str(final) + '[shape="box"]\n')

        for state_index, state in enumerate(self.states):
            for edge in state.edges:
                disp = '(eps)' if edge.val == 0 else edge.val
                f.write('\t' + str(state_index) + ' -> ' + str(edge.dst)
                        + ' [label="' + disp + '"];\n')
        f.write('}\n')

    def from_regex(regex: str):
        from regex import parse
        from nfa_to_dfa import convert
        return convert(parse(regex))
