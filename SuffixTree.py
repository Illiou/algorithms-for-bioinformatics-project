import json
from math import floor
from operator import itemgetter


class Node:
    __slots__ = ("start", "end", "string_id", "string_pos", "children", "terminal_edge_ids", "parent", "path_label_length")

    def __init__(self, start=None, end=None, string_id=None, string_pos=None, children=None):
        """
        Args:
            start: start position in string string_id, representing string written to the edge going towards this node
            end: end position in string string_id, representing string written to the edge going towards this node
            string_id: string id (list pos) to whom start and end correspond to
            string_pos: only in leaf nodes, to string_id corresponding list representing the suffix starting at this position
            children: Node or list of Nodes being children of this Node
        """
        self.start = start
        self.end = end
        self.string_id = [string_id] if string_id is not None else None
        self.string_pos = [string_pos] if string_pos is not None else None
        self.children = []
        if children is not None:
            self.add_children(children)
        self.terminal_edge_ids = None

        self.parent = None
        self.path_label_length = 0

    def __repr__(self):
        return f"{self.string_id[0]}[{self.start}:{self.end}]"

    def add_children(self, children: "Node"):  # type annotation just for PyCharm...
        """add child(ren) and return the last one"""
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

    def add_terminal_edge_ids(self, ids):
        """pass iterable of string ids that have terminal edges outgoing from this node"""
        if self.terminal_edge_ids is None:
            self.terminal_edge_ids = set()
        self.terminal_edge_ids.update(ids)


TERMINATION_SYMBOL = "$"


class SuffixTree:
    __slots__ = ("strings", "root", "_add_string", "track_terminal_edges", "leaves")

    def __init__(self, strings=None, construction_method="naive", track_terminal_edges=False, verbose=False):
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
                                split_node = current_node.add_children(Node(child.start, label_pos, child.string_id[0]))
                                split_node.add_children(current_node.children.pop(child_id))
                                child.set_start(label_pos)
                                if self.track_terminal_edges and child_string[label_pos] == TERMINATION_SYMBOL:
                                    split_node.add_terminal_edge_ids(child.string_id)
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
                    current_node.parent.add_terminal_edge_ids([string_id])
            else:  # ...or add new leaf node
                new_leaf = current_node.add_children(Node(i + suffix_pos, len(string), string_id, i))
                self.leaves.append(new_leaf)
                if self.track_terminal_edges and suffix_pos == len(suffix) - 1:
                    current_node.add_terminal_edge_ids([string_id])
            if verbose:
                print(self, "\n")

    def _add_string_ukkonen(self, string, string_id, verbose=False):
        raise NotImplementedError("Ukkonen not yet implemented, pass construction_method=\"naive\" to SuffixTree")

    def find_suffix_matches_for_prefix(self, prefix_string_id):
        """
        Finds the length of the longest suffix-prefix match between the given prefix string and all other suffixes
        in the tree.
        Args:
            prefix_string_id: prefix_string_id: string_id of the string whose prefix will be tried to be matched
        Returns: list of maximally matched length for each string in the tree
        """
        current_node = self.root
        prefix_pos = 0
        strings_match_lengths = {string_id: 0 for string_id in range(len(self.strings))}
        while len(current_node.children) > 0:
            for child in current_node.children:
                child_string = self.strings[child.string_id[0]]
                # update maximal path length for each string with terminal edges from current_node
                if child_string[child.start:child.end] == TERMINATION_SYMBOL:
                    for string_id in child.string_id:
                        strings_match_lengths[string_id] = max(strings_match_lengths[string_id], current_node.path_label_length)
                # look for child with prefix matching label to continue traversal
                if self.strings[prefix_string_id][prefix_pos] == child_string[child.start]:
                    new_prefix_pos = prefix_pos + child.end - child.start
                    new_node = child
            prefix_pos = new_prefix_pos
            current_node = new_node
        # remove prefix itself
        strings_match_lengths.pop(prefix_string_id, None)
        return strings_match_lengths

    def find_suffix_matches_for_prefix_with_mismatches(self, prefix_string_id, max_mismatch_rate):
        """
        Returns the length of the longest suffix-prefix match between the given prefix string and all other suffixes
        in the tree with a certain allowed mismatch percentage.
        Args:
            prefix_string_id: string_id of the string whose prefix will be tried to be matched
            max_mismatch_rate: number in 0..1 specifying the maximally allowed mismatch percentage
        Returns: list of maximally matched length for each string in the tree
        """
        prefix_string = self.strings[prefix_string_id]
        # maximally possible mismatch count no matter the length of the match
        max_mismatch_count = floor(len(prefix_string) * max_mismatch_rate)
        # [(prefix_pos, mismatch_count, Node), ...]
        candidate_nodes = [(0, 0, self.root)]
        strings_match_lengths = {string_id: 0 for string_id in range(len(self.strings))}
        while len(candidate_nodes) > 0:
            # continue search at the state we were at while adding this candidate node
            node_prefix_pos, node_mismatch_count, current_node = candidate_nodes.pop()
            # try to match prefix string with all children
            for child in current_node.children:
                prefix_pos = node_prefix_pos
                mismatch_count = node_mismatch_count
                child_string = self.strings[child.string_id[0]]
                label_pos = child.start
                # match label of child node with prefix string one by one until max_mismatch_count exceeded or next node reached
                while mismatch_count <= max_mismatch_count:
                    # check if next node reached and if so add it to candidates
                    if label_pos >= child.end:
                        candidate_nodes.append((prefix_pos, mismatch_count, child))
                        break
                    # check if end of suffix
                    if child_string[label_pos] == TERMINATION_SYMBOL:
                        suffix_length = child.path_label_length - 1
                        # check if matched suffix is still within max_mismatch_rate considering it's length
                        if suffix_length > 0 and mismatch_count / suffix_length <= max_mismatch_rate:
                            for string_id in child.string_id:
                                # update maximally matched length for all strings that have suffix ending here
                                strings_match_lengths[string_id] = max(strings_match_lengths[string_id], suffix_length)
                        break
                    # increment mismatch count if no match
                    if prefix_string[prefix_pos] != child_string[label_pos]:
                        mismatch_count += 1
                    prefix_pos += 1
                    label_pos += 1
        # remove prefix itself
        strings_match_lengths.pop(prefix_string_id, None)
        return strings_match_lengths

    def find_most_common_suffixes(self):
        """
        Traverses the whole tree to find the suffix with the most terminal edge ids on the path
        Returns: list of the form [(number_of_terminal_edge_ids_on_path, suffix_length, Node), ...] ordered by
        most terminal edges and then suffix length
        """
        # [(number_of_terminal_edge_ids_on_path, suffix_length, Node), ...]
        recorded_leaves = []
        # [(terminal_edge_ids_on_path, Node), ...]
        nodes_left = [(set(), self.root)]
        while len(nodes_left) > 0:
            terminal_edge_ids_on_path, node = nodes_left.pop()
            nodes_to_be_added = []
            leaves_to_be_added = []
            for child in node.children:
                if self.strings[child.string_id[0]][child.start:child.end] == TERMINATION_SYMBOL:
                    if node is self.root:
                        continue  # skip leaf on root with termination symbol
                    terminal_edge_ids_on_path.update(child.string_id)
                if len(child.children) > 0:
                    nodes_to_be_added.append(child)
                else:
                    leaves_to_be_added.append(child)
            nodes_left.extend((terminal_edge_ids_on_path.copy(), node) for node in nodes_to_be_added)
            recorded_leaves.extend((len(terminal_edge_ids_on_path.union(leaf.string_id)), leaf.path_label_length - 1, leaf)
                                   for leaf in leaves_to_be_added)
        recorded_leaves.sort(key=itemgetter(0, 1), reverse=True)
        return recorded_leaves

    def __repr__(self):
        # needed to remove circularity
        def remove_parent(o):
            if isinstance(o, set):
                return list(o)
            d = o.__dict__.copy()
            if isinstance(o, Node):
                d.pop("parent", None)
            return d
        return json.dumps(self, default=lambda o: remove_parent(o), indent=4)

    def render_children(self, node, root_label=False):
        if root_label:
            if node.terminal_edge_ids is not None and len(node.terminal_edge_ids) > 0:
                label = f"({min(node.terminal_edge_ids)}..{max(node.terminal_edge_ids)})"
            else:
                label = "()"
        else:
            label = f"|-{self.strings[node.string_id[0]][node.start:node.end]}"
            if node.terminal_edge_ids is not None and len(node.terminal_edge_ids) > 0:
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
        # [(number of sequence occurrences, sequence), ...]
        unique_sequences = []
        for leaf in self.leaves:
            # if that suffix represents a whole sequence, count all of the sequences ending here
            if leaf.path_label_length == len(self.strings[leaf.string_id[0]]):
                unique_sequences.append((len(leaf.string_id), self.strings[leaf.string_id[0]][:-1]))
        unique_sequences.sort(key=itemgetter(0), reverse=True)
        return unique_sequences


if __name__ == '__main__':
    # test_string = ["axbcd", "dxbcd", "xbcda", "bxbcd"]
    # test_string = ["cba", "dcb", "edc"]
    test_string = ["CTCGTACGACTCTTAGCGGTGGATCACTCGGCTCGTGCGGGGAATTCTCG",
"CGCGACCTCAGATCAGACGTGGCGACCCGCTGAATTTAAGCTGGAATTCT",
"TCGCGTGATGACATTCTCCGGAATCGCTGTACGGCCTTGATGAAAGCACA",
"ACGTTAGGTCAAGGTGTAGCTGGAATTCTCGGGTGCCAAGGAACTCCCGT",
"ACGGAGCCTGGAATTCTCGGGTGCCAAGGCACTCCAGTCACACAGTGATC",
"TTCAAGTAATCCAGGATAGGCATGGAATTCTCGGGTGCCAAGGAACTCCA",
"CCTGGATGATGATAAGCAAATGCTGACTGAACATGAAGGTCTTAATTAGC",
"TTTCTATGATGAATCAAACTAGCTCACTATGACCGACAGTGAAAATACAT",
"TGGAATTCTCGGGAGCCAAGGAACTCCAGTAAAACAGGGATCTCGTATGC",
"TTTCTATGATGAATCAAACTAGCTCACTATGACCGACAGTGAAAATACAT",]
    tree = SuffixTree(test_string, construction_method="naive", track_terminal_edges=True, verbose=False)
    print(repr(tree))
    print(tree)
    print(tree.find_most_common_suffixes())
