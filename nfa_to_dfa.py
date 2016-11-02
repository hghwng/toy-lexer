#!/usr/bin/env python3
from fsa import FSA
from collections import defaultdict


class _NFAToDFA:
    def convert(self, nfa: FSA, final_sets=None):
        self.nfa = nfa
        self.closure_array = self.init_closure()
        set_graph = self.nfa_to_dfa_set_graph()
        return self.dfa_set_graph_to_dfa(set_graph, final_sets)

    def init_closure(self):
        result = [{i} for i in range(len(self.nfa.states))]
        changed = True
        while changed:
            changed = False
            for i in range(len(self.nfa.states)):
                closure = set(result[i])
                for edge in self.nfa.states[i].edges:
                    if edge.val == 0:
                        closure.update(result[edge.dst])
                if closure != result[i]:
                    result[i] = closure
                    changed = True
        return result

    def closure(self, states):
        if hasattr(states, '__next__'):
            result = set()
            for state in states:
                result |= self.closure_array[state]
            return result
        else:
            return self.closure_array[states]

    def get_dst_sets(self, src_states):
        result = defaultdict(set)  # result[val] = dst_states
        for state in src_states:
            for edge in self.nfa.states[state].edges:
                if edge.val != 0:
                    result[edge.val].update(self.closure(edge.dst))
        return result

    def nfa_to_dfa_set_graph(self):
        set_graph = dict()  # set_graph[src_set][val] = dst_set

        set_new = {frozenset(self.closure(0))}
        while set_new:
            set_proc = set_new.pop()
            dst_sets = self.get_dst_sets(set_proc)
            set_graph[set_proc] = dst_sets
            for dst_set in dst_sets.values():
                frozen_dst_set = frozenset(dst_set)
                if frozen_dst_set not in set_graph:
                    set_new.add(frozen_dst_set)
        return set_graph

    def debug_print_set_graph(self, set_graph):
        for src, edges in set_graph.items():
            for val, dst in edges.items():
                print(set(src), val, set(dst))

    def dfa_set_graph_to_dfa(self, set_graph, final_sets):
        dfa = FSA()

        # Label the sets
        set_label = dict()
        new_final_sets = [set() for i in range(len(final_sets))]
        for index, state in enumerate(set_graph):
            for final_set_index, final_set in enumerate(final_sets):
                in_final = final_set.intersection(state)
                if len(in_final) == 0:
                    if 0 in state:
                        set_label[state] = 0
                    else:
                        set_label[state] = dfa.add_state()
                else:
                    if 0 in state:
                        set_label[state] = 0
                        dfa.add_final(0)
                        new_final_sets[final_set_index].add(0)
                    else:
                        new_state = dfa.add_final_state()
                        set_label[state] = new_state
                        new_final_sets[final_set_index].add(new_state)
                    # High priority final set is found
                    break

        # Add the edges
        for src_state_set, src_state in set_graph.items():
            for val, dst_state_set in src_state.items():
                src_label = set_label[frozenset(src_state_set)]
                dst_label = set_label[frozenset(dst_state_set)]
                dfa.add_edge(src_label, dst_label, val)

        return dfa, new_final_sets


def convert(nfa: FSA, final_sets=None):
    if final_sets is None:
        return _NFAToDFA().convert(nfa, (set(nfa.finals),))[0]
    return _NFAToDFA().convert(nfa, final_sets)


def main():
    import sys
    import regex
    nfa = regex.parse(sys.argv[1])
    nfa.dump(open('nfa.dot', 'w'))
    dfa = convert(nfa)
    dfa.dump(open('dfa.dot', 'w'))

if __name__ == '__main__':
    main()
