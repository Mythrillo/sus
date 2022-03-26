from typing import Any
import math


class DecisionTable:

    def __init__(self, filename: str, delimiter: str = ",") -> None:
        self.table: list[list[Any]] = self._load_decision_table(filename, delimiter)
        self.attributes_appearance = self._count_attributes_appearance()
        self._decisions = self.attributes_appearance[-1]
        self.entropy = self._calculate_entropy()

    def _load_decision_table(self, filename: str, delimiter: str) -> list[list[Any]]:
        table = []
        with open(filename, "r") as f:
            for row in f:
                table.append(row.strip().split(delimiter))
        return table

    def _count_attributes_appearance(self) -> list[dict[Any, int]]:
        res = []
        for i in range(len(self.table[0])):
            tmp = {}
            for row in self.table:
                if row[i] in tmp:
                    tmp[row[i]] += 1
                else:
                    tmp[row[i]] = 1
            res.append(tmp)
        return res

    def _calculate_entropy(self) -> float:
        entropy = 0
        for _, appearance in self._decisions.items():
            prob = appearance / len(self.table)
            entropy += prob * math.log(prob, 2)
        return -1 * entropy

