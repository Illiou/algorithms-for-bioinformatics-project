import json
import numpy as np

def make_list_or_none(v):
    if v is None:
        return None
    if not isinstance(v, list):
        return [v]
    return v


def make_set_or_empty_set(v):
    if v is None:
        return set()
    if hasattr(v, "__iter__"):
        return set(v)
    return {v}


class Node:
    def __init__(self, start=None, end=None, string_id=None, string_pos=None, children=None, terminal_edge_ids=None):
        """
        Args:
            start: start position in string string_id, representing string written to the edge going towards this node
            end: end position in string string_id, representing string written to the edge going towards this node
            string_id: list of string id (list pos) to whom start and end correspond to
            string_pos: only in leaf nodes, to string_id corresponding list representing the suffix starting at this position
            children: Node or list of Nodes being children of this Node
            terminal_edge_ids: string or set of string ids that have terminal edges outgoing from this node
        """
        self.start = start
        self.end = end
        self.string_id = make_list_or_none(string_id)
        self.string_pos = make_list_or_none(string_pos)
        self.children = []
        self.add_children(children)
        self.terminal_edge_ids = make_set_or_empty_set(terminal_edge_ids)

        self.parent = None
        self.path_label_length = 0

    def __repr__(self):
        s = str(self.string_id[0]) +'['+ str(self.start) + ':'+ str(self.end) +']'

        return s

    def add_children(self, children: "Node"):  # type annotation just for PyCharm...
        """add child(ren) and return the last one"""
        if children is None:
            return None
        if not isinstance(children, list):
            children = [children]

        self.children.extend(children)
        for child in children:
            child.parent = self
            child.update_path_label_length()
        return self.children[-1]

    def add_string_to_leaf(self, string_id, string_pos):
        self.string_id.append(string_id)
        self.string_pos.append(string_pos)

    def set_start(self, start):
        self.start = start
        self.update_path_label_length()

    def set_end(self, end):
        self.end = end
        self.update_path_label_length()

    def update_path_label_length(self):
        self.path_label_length = self.parent.path_label_length + self.end - self.start


TERMINATION_SYMBOL = "$"


class SuffixTree:
    def __init__(self, strings=None, construction_method="ukkonen", track_terminal_edges=False, verbose=False):
        """
        Args:
            strings: string or list of strings to be added to the suffix tree
            construction_method: select construction method between "ukkonen" and "naive"
            track_terminal_edges: keep track of terminal edges for every internal node
            verbose: if true print Suffix Tree on every construction iteration
        """
        if strings is None:
            self.strings = []
        else:
            if not isinstance(strings, list):
                strings = [strings]
            self.strings = [s + TERMINATION_SYMBOL for s in strings]
        self.root = Node()
        self._add_string = self._add_string_naive if construction_method == "naive" else self._add_string_ukkonen
        self.track_terminal_edges = track_terminal_edges
        self.leaves = []  # list of leaves in tree

        self._construct(verbose)

    def add_string(self, string, verbose=False):
        """adds single string to SuffixTree and returns it's string_id"""
        string = string + TERMINATION_SYMBOL
        self.strings.append(string)
        string_id = len(self.strings) - 1
        self._add_string(string, string_id, verbose)
        return string_id

    def _construct(self, verbose=False):
        for string_id, string in enumerate(self.strings):
            self._add_string(string, string_id, verbose)

    def _add_string_naive(self, string, string_id, verbose=False):
        for i in range(len(string)):  # add suffix i..m
            suffix = string[i:]
            current_node = self.root
            suffix_pos = 0
            node_found = False
            # find node to add leaf node on
            while not node_found:
                # find child node with matching label
                for child_id, child in enumerate(current_node.children):
                    child_string = self.strings[child.string_id[0]]
                    # check first label character of current node
                    if suffix[suffix_pos] == child_string[child.start]:
                        # check rest of the label
                        suffix_pos += 1
                        for label_pos in range(child.start + 1, child.end):
                            # splitting point?
                            if suffix[suffix_pos] != child_string[label_pos]:
                                # add splitting node
                                split_node = current_node.add_children(Node(child.start, label_pos, child.string_id))
                                split_node.add_children(current_node.children.pop(child_id))
                                child.set_start(label_pos)
                                if self.track_terminal_edges and child_string[label_pos] == TERMINATION_SYMBOL:
                                    split_node.terminal_edge_ids.update(child.string_id)
                                # to add leaf node
                                current_node = split_node
                                node_found = True
                                break
                            suffix_pos += 1
                        # matched until next node, repeat process
                        else:
                            current_node = child
                        break
                # no child matched rest of suffix
                else:
                    node_found = True
            # add string_id to existing leaf node...
            if suffix_pos == len(suffix):
                current_node.add_string_to_leaf(string_id, i)
                if self.track_terminal_edges and current_node.end - current_node.start == 1:
                    current_node.parent.terminal_edge_ids.add(string_id)
            else:  # ...or add new leaf node
                new_leaf = current_node.add_children(Node(i + suffix_pos, len(string), string_id, i))
                self.leaves.append(new_leaf)
                if self.track_terminal_edges and suffix_pos == len(suffix) - 1:
                    current_node.terminal_edge_ids.add(string_id)
            if verbose:
                print(self, "\n")

    def _add_string_ukkonen(self, string, string_id, verbose=False):
        raise NotImplementedError("Ukkonen not yet implemented, pass construction_method=\"naive\" to SuffixTree")

    def find_suffix_matches_for_prefix(self, prefix_string_id):
        current_node = self.root
        prefix_pos = 0
        string_stacks = {}
        while len(current_node.children) > 0:
            # add current terminal edge string ids to stack
            for string_id in current_node.terminal_edge_ids:
                string_stacks.setdefault(string_id, [])
                string_stacks[string_id].append(current_node)
            # look for child with prefix matching label
            for child in current_node.children:
                child_string = self.strings[child.string_id[0]]
                if self.strings[prefix_string_id][prefix_pos] == child_string[child.start]:
                    assert self.strings[prefix_string_id][prefix_pos:].find(child_string[child.start:]) == 0
                    prefix_pos += child.end - child.start
                    current_node = child
                    break
            else:
                raise AssertionError("didn't find prefix in tree")
        # record how far each string matched into the prefix string
        prefix_match_pos = {}
        for string_id in range(len(self.strings)):
            stack = string_stacks.get(string_id)
            prefix_match_pos[string_id] = stack[-1].path_label_length if stack is not None and len(stack) > 0 else 0
        # remove prefix itself
        prefix_match_pos.pop(prefix_string_id, None)
        return prefix_match_pos

    def most_common_adaptersequence(self):
        """Most common adapter sequence is suffix with most amount of terminal labels on the path"""

        number_terminal_edges = []  # counts for every leave node how many terminal edges are on the path to the root
        suffixes = []  # stores the whole suffix for every leave node

        to_be_processed = [n for n in self.leaves]
        while len(to_be_processed) > 0:
            node = to_be_processed.pop()
            terminal_edges_on_path = []  # stores how many strings end on this path

            # prevent that the leave '$' where obviously all strings go through is taken as most common suffix
            if node.end - node.start > 1:
                terminal_edges_on_path.extend(node.string_id)

            if isinstance(node.string_id, list):
                string_id = node.string_id[0]
            else:
                string_id = node.string_id
            suffix = self.strings[string_id][-node.path_label_length::]

            # go from leave through whole branch to the root and count the terminal edges on the way
            while node.parent is not self.root:
                for element in node.terminal_edge_ids:
                    if element not in terminal_edges_on_path:  # prevent doubles bc later we only look at length of list
                        terminal_edges_on_path.append(element)
                node = node.parent

            suffixes.append(suffix)
            number_terminal_edges.append(len(terminal_edges_on_path))

        # path with most terminal edges is the most probable adapter sequence
        max_value = max(number_terminal_edges)
        if max_value == 1:
            return None
        else:
            index_max = number_terminal_edges.index(max_value)
            max_suffix = suffixes[index_max]
            return max_suffix[:-1]

    def __repr__(self):
        # needed to remove circularity
        def remove_parent(o):
            if isinstance(o, set):
                return list(o)
            d = o.__dict__
            if isinstance(o, Node):
                d.pop("parent", None)
            return d
        return json.dumps(self, default=lambda o: remove_parent(o), indent=4)

    def render_children(self, node, root_label=False):
        if root_label:
            label = f"({', '.join(str(n) for n in node.terminal_edge_ids)})"
        else:
            label = f"|-{self.strings[node.string_id[0]][node.start:node.end]}"
            if self.track_terminal_edges and len(node.terminal_edge_ids) > 0:
                label += f" ({', '.join(str(n) for n in node.terminal_edge_ids)})"
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
            return [f"{label}\t\t\t{strings}"]

    def __str__(self):
        return "\n ".join(self.render_children(self.root, root_label=True))


    def find_barcodes(self):
        """Basis idea: After removing the adapter sequence, barcodes are the longest commonly occuring suffixes of
        the sequences. Moreover, this algorithm assumes that the minimum barcode length is 4 and the maximum 8. It does not assume
        that all barcodes have the same length."""

        number_of_sequences = [0]*len(self.strings)  # i-th entry stores number of sequences that share this suffix of string i
        suffixes = [0]*len(self.strings)   # i-th entry stores this suffix of string i
        len_suffixes = [0]*len(self.strings)  # i-th entry stores length of this suffix of string i

        for node in self.leaves:

            if isinstance(node.string_id, list):
                string_id = node.string_id[0]
                suffix = self.strings[string_id][-node.path_label_length:-1]
                # neglect '$' leave and also suffixes that are shorter then 4
                if len(suffix) < 4:
                    continue
                # check if more strings then for other suffix of that string end in this suffix, if its more then this is the most probable barcode at the moment
                if len(node.string_id) > number_of_sequences[string_id]:
                    for id in node.string_id:
                        number_of_sequences[id] = len(node.string_id)
                        suffixes[id] = suffix
                        len_suffixes[id] = len(suffix)
                # if its the same number but the length is longer this is the most probable barcode at the moment:
                elif len(node.string_id) == number_of_sequences[string_id] and len_suffixes[string_id] > len_suffixes[string_id]:
                    for id in node.string_id:
                        number_of_sequences[id] = len(node.string_id)
                        suffixes[id] = suffix
                        len_suffixes[id] = len(suffix)
                # else, a suffix before was better
            else:
                id = node.string_id
                suffix = self.strings[id][-node.path_label_length:-1]
                # neglect '$' leave and also suffixes that are shorter then 4
                if len(suffix) < 4:
                    continue
                # check if more strings then before end in this suffix, if its more then this is the most probable barcode at the moment
                if 1 > number_of_sequences[string_id]:
                    number_of_sequences[id] = 1
                    suffixes[id] = suffix
                    len_suffixes[id] = len(suffix)
                # if its the same number but the length is longer this is the most probable barcode at the moment:
                elif 1 == number_of_sequences[id] and len_suffixes[id] > len_suffixes[id]:
                    number_of_sequences[id] = 1
                    suffixes[id] = suffix
                    len_suffixes[id] = len(suffix)
            # else, a suffix before was better

        # all barcodes have the same length, so the length that appears most often is the length of the barcodes
        length = max(set(len_suffixes), key=len_suffixes.count)
        j = 0
        for i in suffixes:
            if i == 0:
                print(self.strings[j])
            j += 1
        barcodes = [suffixes[n][-length:] for n in range(len(suffixes))]
        number_sequences_per_sample = {x: barcodes.count(x) for x in barcodes}
        sequences_per_sample = {x:[] for x in barcodes}
        i = 0
        for suffix in suffixes:
            sequences_per_sample[suffix[-length:]].append(self.strings[i][:-length])
            i += 1
        length_of_sequences = {x:[] for x in barcodes}
        for string_id in range(len(self.strings)):
            length_of_sequences[barcodes[string_id]].append(len(self.strings[string_id]))

        return set(barcodes), sequences_per_sample, number_sequences_per_sample, length_of_sequences

    def count_unique_sequences(self):
        """Counts the amount of unique sequences in the tree."""
        counts = {}
        for leave in self.leaves:
            # if that suffix represents the whole sequence, count all of those sequences
            if leave.path_label_length == len(self.strings[leave.string_id[0]]):
                counts[self.strings[leave.string_id[0]]] = len(leave.string_id)
        return counts


if __name__ == '__main__':
    test_string = ["acc", "bcc", "ccg"]
    tree = SuffixTree(test_string, construction_method="naive", track_terminal_edges=True, verbose=True)
    print(repr(tree))
    print(tree)
