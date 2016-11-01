#!/usr/bin/env python3


class UnionSet:
    def __init__(self, num):
        self._arr = [i for i in range(num)]

    def find(self, i):
        while self._arr[i] != self._arr[self._arr[i]]:
            self._arr[i] = self._arr[self._arr[i]]
        return self._arr[i]

    def union(self, i, j):
        self._arr[self.find(i)] = self.find(j)

    def to_closure(self):
        closure = [None] * len(self._arr)
        for i in range(len(self._arr)):
            root = self.find(i)
            if closure[root] is None:
                closure[root] = {i}
            else:
                closure[root].add(i)
            closure[i] = closure[root]
        return closure
