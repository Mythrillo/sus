from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Any

# Written using Python 3.10.2


class DecisionTable:
    def __init__(self, table: list[list[Any]], attribute: Any = None) -> None:
        self._setup(table)
        self.answer: dict = {}
        self.decision: dict = {}
        self.children: list[DecisionTable] = []
        self.attribute = attribute
        self.column: int = 0

    def _setup(self, table: list[list[Any]]) -> None:
        self.table: list[list[Any]] = table
        self._rows_count: int = len(self.table)
        self.attributes_appearance: list[dict[Any, int]] = self._count_attributes_appearance(self.table)
        self._decision_classes = list(self.attributes_appearance[-1].keys())
        self.entropy: float = self._calculate_entropy(self.table)

    def _load_decision_table(self, filename: str, delimiter: str) -> list[list[Any]]:
        table = []
        with open(filename, "r") as f:
            for row in f:
                table.append(row.strip().split(delimiter))
        return table

    def _count_attributes_appearance(self, table: list[list[Any]]) -> list[dict[Any, int]]:
        res = []
        for i in range(len(table[0])):
            tmp = {}
            for row in table:
                if row[i] in tmp:
                    tmp[row[i]] += 1
                else:
                    tmp[row[i]] = 1
            res.append(tmp)
        return res

    def _calculate_entropy(self, table: list[list[Any]], column: int = -1) -> float:
        entropy = 0
        attributes_appearances = self._count_attributes_appearance(table)
        decisions = attributes_appearances[column]
        for _, appearance in decisions.items():
            prob = appearance / len(table)
            entropy += prob * math.log(prob, 2)
        return -1 * entropy

    def _calculate_information(self, column_attributes: dict[Any, int], column: int) -> float:
        info = 0
        for attribute, count in column_attributes.items():
            new_table = self._create_new_table(attribute, column)
            info += (count / self._rows_count) * self._calculate_entropy(new_table)
        return info

    def _create_new_table(self, attribute: Any, column: int) -> list[list[Any]]:
        new_table = []
        for row in self.table:
            if attribute == row[column]:
                new_table.append(row)
        return new_table

    def _calculate_split_info(self, column: int) -> float:
        return self._calculate_entropy(self.table, column)

    def _calculate_gain_ratio(self, info: float, column: int) -> float:
        return (self.entropy - info) / self._calculate_split_info(column)

    def _choose_attribute(self, attributes_appearance: list[dict[Any, int]]) -> tuple[Any, int]:
        chosen = None
        biggest_ratio = -1
        column = -1
        for i, x in enumerate(attributes_appearance):
            info = self._calculate_information(x, i)
            try:
                gain_ratio = self._calculate_gain_ratio(info, i)
            except ZeroDivisionError:
                continue
            if gain_ratio > biggest_ratio:
                biggest_ratio = gain_ratio
                chosen = x
                column = i
        return chosen, column

    def _stop_criterion_met(self) -> bool:
        if self.table == []:
            return True
        elif len(self._decision_classes) == 1:
            self.decision = self._decision_classes[0]
            return True
        return False

    def main_recursion(self) -> None:
        # Doesn't work for larger datasets
        if not self._stop_criterion_met():
            chosen, self.column = self._choose_attribute(self.attributes_appearance[:-1])
            self.decision = chosen
            for attribute in chosen:
                new_table = self._create_new_table(attribute, self.column)
                self.children.append(DecisionTable(new_table, attribute))
        self.answer[self.column] = {}
        for children in self.children:
            children.main()
            if type(children.decision) == str:
                self.answer[self.column][children.attribute] = children.decision
            else:
                self.answer = self.answer | children.answer

    def main(self) -> None:
        global DTS
        if not self._stop_criterion_met():
            chosen, self.column = self._choose_attribute(self.attributes_appearance[:-1])
            self.decision = chosen
            for attribute in chosen:
                new_table = self._create_new_table(attribute, self.column)
                new_d = DecisionTable(new_table, attribute)
                DTS.append(new_d)
                self.children.append(new_d)
        self.answer[self.column + 1] = {}

    def gather_answers(self) -> None:
        for children in self.children:
            if type(children.decision) == str:
                self.answer[self.column + 1][children.attribute] = children.decision
            else:
                self.answer[self.column + 1][children.attribute] = children.answer


def _load_data(filename: str, delimiter: str = ",") -> list[list[Any]]:
    table = []
    with open(filename, "r") as f:
        for row in f:
            table.append(row.strip().split(delimiter))
    return table


# Code below was created by prof. Jan Kozak - University of Economics in Katowice and modified by me.
# The code was shared during class: `Systemy uczące się``, and is mostly used to visualize the solution for easier
# comparison to correct output. My representation can be found in the `answer.json` file that is created during script
# execution.
@dataclass
class Node:
    children = None
    attribute = None
    value = None
    decison_class = None


def _show_tree(tree, indent) -> None:
    if tree.attribute is not None:
        print(" " * indent, end="")
        if tree.value:
            print(tree.value, end=" -> ")
        print("Atrybut", tree.attribute)
        for p in tree.children:
            _show_tree(p, indent + 4)
    else:
        print(" " * indent, end="")
        print(tree.value, "->", tree.decision_class)


def _build_tree(answer) -> Node:
    w = Node()
    w.children = []
    key, element = answer.popitem()
    w.attribute = key
    for t in element:
        if isinstance(element[t], dict):
            new_node = _build_tree(element[t])
            new_node.value = t
            w.children.append(new_node)
        else:
            new_node = Node()
            new_node.value = t
            new_node.decision_class = element[t]
            w.children.append(new_node)
    return w


if __name__ == "__main__":
    DTS = []
    dt = _load_data("car.data")
    DTS.append(DecisionTable(dt))
    for d in DTS:
        d.main()
    for d in reversed(DTS):
        d.gather_answers()
    with open("answer.json", "w") as f:
        json.dump(DTS[0].answer, f, indent=2)
    w = _build_tree(DTS[0].answer)
    _show_tree(w, 0)
