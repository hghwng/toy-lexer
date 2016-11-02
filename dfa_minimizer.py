#!/usr/bin/env python3
from fsa import FSA


class _Minimizer:
    def minimize(self, dfa: FSA, final_sets):
        self.dfa = dfa
        self.final_sets = final_sets
        self.affect = [[list() for j in range(len(self.dfa.states))]
                       for i in range(len(self.dfa.states))]
        self.combinable = [[True] * len(self.dfa.states)
                           for i in range(len(self.dfa.states))]
        self.mark_uncombinable()
        self.calculate_dependency()
        new_states, to_new_state = self.relabel()
        return self.build_min_dfa(new_states, to_new_state)

    def mark_uncombinable(self):
        final_states = set()
        for final_set in self.final_sets:
            final_states.update(final_set)
        nonfinal_states = set(range(len(self.dfa.states))) - final_states
        uncombinable_sets = list(self.final_sets)
        uncombinable_sets.append(nonfinal_states)

        for x in range(len(uncombinable_sets)):
            x_set = uncombinable_sets[x]
            for y in range(x + 1, len(uncombinable_sets)):
                y_set = uncombinable_sets[y]
                for x_elem in x_set:
                    for y_elem in y_set:
                        if x_elem > y_elem:
                            self.combinable[y_elem][x_elem] = False
                        else:
                            self.combinable[x_elem][y_elem] = False

    def mark(self, i, j):
        if self.combinable[i][j] is False:
            return

        self.combinable[i][j] = False
        for x, y in self.affect[i][j]:
            self.mark(x, y)

    def process_state(self, x, y):
        x_edges = dict([(t.val, t.dst) for t in self.dfa.states[x].edges])
        y_edges = dict([(t.val, t.dst) for t in self.dfa.states[y].edges])
        if x_edges.keys() != y_edges.keys():
            self.mark(x, y)
            return

        dependency = list()
        for val, x_edge in x_edges.items():
            x_dst = x_edges[val]
            y_dst = y_edges[val]
            if x_dst == y_dst:
                continue
            if x_dst > y_dst:
                x_dst, y_dst = y_dst, x_dst
            if self.combinable[x_dst][y_dst]:
                dependency.append((x_dst, y_dst))
            else:
                self.mark(x, y)
                return

        for x_dst, y_dst in dependency:
            self.affect[x_dst][y_dst].append((x, y))

    def calculate_dependency(self):
        for i in range(len(self.dfa.states)):
            for j in range(i + 1, len(self.dfa.states)):
                self.process_state(i, j)

    def relabel(self):
        processed = [False] * len(self.dfa.states)
        to_new_state = [-1] * len(self.dfa.states)
        new_states = list()
        for i in range(len(self.dfa.states)):
            if processed[i]:
                continue
            processed[i] = True
            new_states.append({i})
            to_new_state[i] = len(new_states) - 1
            for j in range(i + 1, len(self.dfa.states)):
                if processed[j]:
                    continue
                if self.combinable[i][j]:
                    processed[j] = True
                    new_states[-1].add(j)
                    to_new_state[j] = len(new_states) - 1
        return new_states, to_new_state

    def build_min_dfa(self, new_states, to_new_state):
        dfa = FSA()
        for i in range(len(new_states) - 1):
            dfa.add_state()

        new_final_sets = [set() for i in range(len(self.final_sets))]
        for src_idx, old_states in enumerate(new_states):
            # Mark the new state if it's in final states
            for final_set_index, final_set in enumerate(self.final_sets):
                if old_states.issubset(final_set):
                    new_final_sets[final_set_index].add(src_idx)
                    dfa.add_final(src_idx)
            # Add the edges
            for edge in self.dfa.states[tuple(old_states)[0]].edges:
                dfa.add_edge(src_idx, to_new_state[edge.dst], edge.val)

        return dfa, new_final_sets


def minimize(dfa: FSA, final_sets=None):
    if final_sets is None:
        return _Minimizer().minimize(dfa, (set(dfa.finals),))[0]
    return _Minimizer().minimize(dfa, final_sets)


def main():
    import sys
    import regex
    import nfa_to_dfa
    nfa = regex.parse(sys.argv[1])
    nfa.dump(open('nfa.dot', 'w'))
    dfa = nfa_to_dfa.convert(nfa)
    dfa.dump(open('dfa.dot', 'w'))
    mindfa, _ = minimize(dfa)
    mindfa.dump(open('mindfa.dot', 'w'))

if __name__ == '__main__':
    main()
