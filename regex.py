#!/usr/bin/env python3
from fsa import FSA

# simple: char | range | '(' regexp ')'
#
# repeating: simple '*'
#          | simple '+'
#          | simple '?'
#          | simple
#
# sequence: repeating
#         | repeating sequence
#
# regexp: sequence '|' regexp
#       | sequence


class _Parser:
    FORBIDDEN_CHAR = "+*?|()[]"

    def parse(self, regex: str):
        self.pos = 0
        self.regex = regex
        self.maxpos = len(self.regex)
        return self.parse_regexp()

    def peek(self):
        if self.pos < len(self.regex):
            return self.regex[self.pos]
        return chr(0)

    def parse_char(self):
        if self.peek() in self.FORBIDDEN_CHAR:
            raise SyntaxError("Unexpected symbol " + self.peek())

        char = self.regex[self.pos]
        if char == '\\':
            char = {'r': '\r', 'n': '\r', 'v': '\v'}.get(
                self.regex[self.pos + 1], self.regex[self.pos + 1])
            self.pos += 1

        self.pos += 1
        return char

    def parse_range(self):
        if self.regex[self.pos] != '[':
            return None
        self.pos += 1

        fsa = FSA()
        final = fsa.add_final_state()

        while self.pos < self.maxpos:
            if self.peek() == ']':
                self.pos += 2
                return fsa
            char = self.parse_char()
            if self.peek() == '-':
                self.parse_char()
                next_char = self.parse_char()
                if ord(next_char) >= ord(char):
                    for i in range(ord(char), ord(next_char) + 1):
                        fsa.add_edge(0, final, chr(i))
            else:
                fsa.add_edge(0, final, char)
        raise SyntaxError("Missing ]")

    def parse_simple(self):
        # Situation: '(' regexp ')'
        if self.peek() == '(':
            pos = self.pos
            self.pos += 1
            if self.peek() == ')':
                self.pos += 1
            else:
                fsa = self.parse_regexp()
                if fsa:
                    if self.peek() != ')':
                        raise SyntaxError("Missing )")
                    else:
                        self.pos += 1
                        return fsa
                else:
                    self.pos = pos

        # Situation: range
        fsa = self.parse_range()
        if fsa:
            return fsa

        # Situation: char
        fsa = FSA()
        final = fsa.add_final_state()
        fsa.add_edge(0, final, self.parse_char())
        return fsa

    def parse_repeating(self):
        subfsa = self.parse_simple()
        fsa = subfsa.duplicate()
        if self.peek() in "*?":
            fsa.add_edge_epsilon(0, fsa.finals[0])
        if self.peek() in "*+":
            fsa.add_edge_epsilon(fsa.finals[0], 0)
        if self.peek() in "*+?":
            self.pos += 1
        return fsa

    def parse_sequence(self):
        fsa = None
        while self.pos < self.maxpos:
            if self.peek() in '|)':
                return fsa
            subfsa = self.parse_repeating()
            if fsa:
                subfsa_begin = fsa.combine(subfsa)
                subfsa_end = fsa.finals.pop()
                fsa.add_edge_epsilon(fsa.finals[0], subfsa_begin)
                fsa.finals[0] = subfsa_end
            else:
                fsa = subfsa
        return fsa

    def parse_regexp(self):
        fsa = FSA()
        final = fsa.add_final_state()

        while self.pos < self.maxpos:
            subfsa = self.parse_sequence()
            if subfsa is None:
                continue
            subfsa_begin = fsa.combine(subfsa)
            subfsa_end = fsa.finals.pop()
            fsa.add_edge_epsilon(0, subfsa_begin)
            fsa.add_edge_epsilon(subfsa_end, final)

            if self.peek() == '|':
                self.pos += 1
                continue
            if self.peek == chr(0) or self.peek() in self.FORBIDDEN_CHAR:
                return fsa

        return fsa


def parse(regex: str) -> FSA:
    parser = _Parser()
    return parser.parse(regex)


def main():
    import sys
    fsa = parse(sys.argv[1])
    fsa.dump(open('regex.dot', 'w'))

if __name__ == '__main__':
    main()
