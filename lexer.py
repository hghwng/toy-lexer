#!/usr/bin/env python3
from fsa import FSA


class LexerFactory:
    def __init__(self, rule_list):
        self._build_dfa(rule_list)

    def _build_dfa(self, rule_list):
        nfa = FSA()
        nfa_final_sets = list()
        for regex, category in rule_list:
            regex_nfa = FSA.from_regex(regex)
            last_pos = len(nfa.finals)
            new_start = nfa.combine(regex_nfa)
            nfa.add_edge_epsilon(0, new_start)
            nfa_final_sets.append(set(nfa.finals[last_pos:]))

        from nfa_to_dfa import convert
        dfa, dfa_final_sets = convert(nfa, nfa_final_sets)
        from dfa_minimizer import minimize
        dfa, dfa_final_sets = minimize(dfa, dfa_final_sets)

        # Convert edge-oriented states to value oriented states
        transitions = [dict() for i in range(len(dfa.states))]
        for src_index, state in enumerate(dfa.states):
            src_transition = transitions[src_index]
            for edge in state.edges:
                src_transition[edge.val] = edge.dst
        self._transitions = transitions

        # Build mapping from state to corresponding category
        final_mapping = [None] * len(dfa.states)
        for index, final_set in enumerate(dfa_final_sets):
            for state in final_set:
                final_mapping[state] = rule_list[index][1]
        self._final_mapping = final_mapping

    def create_lexer(self, buf: str):
        return Lexer(self._transitions, self._final_mapping, buf)


class Lexer:
    def __init__(self, transitions: list, final_mapping: list, buf: str):
        self._transitions = transitions
        self._final_mapping = final_mapping
        self.reset(buf)

    def reset(self, buf: str):
        self._buf = buf
        self._pos = 0
        self._len = len(buf)

    def next(self):
        state = 0
        success_pos = self._pos
        success_category = None
        for pos in range(self._pos, self._len):
            val = self._buf[pos]
            if val in self._transitions[state]:
                state = self._transitions[state][val]
                if self._final_mapping[state] is not None:
                    success_pos = pos + 1
                    success_category = self._final_mapping[state]
            else:
                break

        string = self._buf[self._pos:success_pos]
        self._pos = success_pos
        return success_category, string


def main():
    import sys
    rules = (('ab|ac', 'KEYWORD'), ('[a-c]+', 'IDENT'), (' +', 'SPACE'))
    lexer_factory = LexerFactory(rules)
    lexer = lexer_factory.create_lexer(sys.argv[1])
    while True:
        cat, string = lexer.next()
        print(cat, repr(string))
        if not cat:
            return

if __name__ == '__main__':
    main()
