import json


class Node:
    def __init__(self, start=None, end=None, string_id=None, string_pos=None, children=None):
        """
        Args:
            start: start position in string string_id, representing string written to the edge going towards this node
            end: end position in string string_id, representing string written to the edge going towards this node
            string_id: list of string id (list pos) to whom start and end correspond to
            string_pos: only in leaf nodes, to string_id corresponding list representing the suffix starting at this position
            children: list of Nodes being children of this Node
        """
        self.start = start
        self.end = end
        self.string_id = self.make_list_or_None(string_id)
        self.string_pos = self.make_list_or_None(string_pos)
        self.children = []
        self.add_children(children)

    @staticmethod
    def make_list_or_None(v):
        if v is None:
            return None
        if not isinstance(v, list):
            return [v]
        return v

    def add_children(self, children):
        """add child(ren) and return the last one"""
        if children is None:
            return None
        if isinstance(children, list):
            self.children.extend(children)
        else:
            self.children.append(children)
        return self.children[-1]

    def add_string_to_leaf(self, string_id, string_pos):
        self.string_id.append(string_id)
        self.string_pos.append(string_pos)


TERMINATION_SYMBOL = "$"


class SuffixTree:
    def __init__(self, strings, construction_method="ukkonen"):
        """
        Args:
            strings: string or list of strings to be added to the suffix tree
            construction_method: select construction method between "ukkonen" and "naive"
        """
        if not isinstance(strings, list):
            strings = [strings]
        self.strings = [s + TERMINATION_SYMBOL for s in strings]
        self.root = Node()
        if construction_method == "naive":
            self._add_string = self._add_string_naive
        else:
            self._add_string = self._add_string_ukkonen

        self._construct()

    def add_string(self, string):
        string = string + TERMINATION_SYMBOL
        self.strings.append(string)
        self._add_string(string, len(self.strings) - 1)

    def _construct(self):
        for string_id, string in enumerate(self.strings):
            self._add_string(string, string_id)

    def _add_string_naive(self, string, string_id):
        for i in range(len(string)):  # add suffix i..m
            suffix = string[i:]
            parent = self.root
            suffix_pos = 0
            node_found = False
            # find node to add leaf node on
            while not node_found:
                # find child node with matching label
                for child_id, child in enumerate(parent.children):
                    child_string = self.strings[child.string_id[0]]
                    # check first label character of current node
                    if suffix[suffix_pos] == child_string[child.start]:
                        # check rest of the label
                        suffix_pos += 1
                        for label_pos in range(child.start + 1, child.end):
                            # splitting point?
                            if suffix[suffix_pos] != child_string[label_pos]:
                                # add splitting node
                                split_node = parent.add_children(Node(child.start, label_pos, child.string_id))
                                split_node.add_children(parent.children.pop(child_id))
                                child.start = label_pos
                                # to add leaf node
                                parent = split_node
                                node_found = True
                                break
                            suffix_pos += 1
                        # matched until next node, repeat process
                        else:
                            parent = child
                        break
                # no child matched rest of suffix
                else:
                    node_found = True
            # add leaf node or add string_id to existing node
            if suffix_pos == len(suffix):
                parent.add_string_to_leaf(string_id, i)
            else:
                parent.add_children(Node(i + suffix_pos, len(string), string_id, i))

    def _add_string_ukkonen(self, string, string_id):
        raise NotImplementedError()

    def __repr__(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    def render_children(self, node, root_label=None):
        if root_label is not None:
            label = root_label
        else:
            label = f"|-{self.strings[node.string_id[0]][node.start:node.end]}"
        if len(node.children) > 0:
            all_lines = []
            for child in node.children:
                lines = self.render_children(child)
                all_lines.extend(lines)
            reached_first_elem = False
            for i in range(len(all_lines) - 1, 0, -1):
                if all_lines[i][0] == "|":
                    reached_first_elem = True
                    endchar = ""
                else:
                    endchar = '|' if reached_first_elem else ' '
                all_lines[i] = f"{' ' * (len(label) + 2)}{endchar}{all_lines[i]}"
            all_lines[0] = f"{label}---{all_lines[0]}"
            return all_lines
        else:
            strings = list(zip(node.string_id, node.string_pos))
            return [f"{label}\t\t{strings}"]

    def __str__(self):
        return "\n ".join(self.render_children(self.root, root_label="()"))


if __name__ == '__main__':
    test_string = ["gctgca", "tgc", "gct"]
    tree = SuffixTree(test_string, construction_method="naive")
    print(repr(tree))
    print(tree)
