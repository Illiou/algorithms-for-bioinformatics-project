class Node:

    """ A suffix-tree Node """

    def __init__(self, chars, parent, outedges, suffixlink, label):
        self.chars = chars  # tuple (startindex, endindex) of prefix on edge or chars
        self.parent = parent  # edge to parent node
        self.outedges = outedges  # list of child nodes
        self.suffixlink = suffixlink
        self.label = label  # tuple (index of word, index of position) for leaf nodes, index of word for internal node

class Naive:
    """ Builds the suffix tree using the naive algorithm"""

    def build(self, word):
        root = Node(None, None, None, None, None)
        wordlabel = 1
        for index in range(len(word)):
            suffix = word[index::] + '$'

            # first insert:
            if root.outedges is None:
                new_node = Node(suffix, root, None, None, (wordlabel, index))
                root.outedges.append(Node)

             # other inserts:
            else:
                # go through all the branches
                for node in root.outedges:
                    # scan if suffix fits on branch
                    i = 0
                    node_word = node.chars
                    while suffix[i] == node_word[i]:  # scan how long suffix fits
                        i += 1

                    if i == 0:  # if it does not fit continue
                        continue

                    else:  # if it fits up to a particular point create a side branch
                        # create 2 new nodes:
                        new_node1 = Node(node_word[i::], node, None, None, node.label)
                        new_node2 = Node(suffix[i::], node, None, None, node.label)

                        # change old node:
                        node.chars = node_word[::i]
                        node.outedges.append(new_node1, new_node2)

class Ukkonen:

    """ Builds the suffix tree using Ukkonens Algorithm"""

    def build(self, word):
        root = Node(None, None, None, None, None)
        actnode = root
        actedge = None
        actlen = 0
        remainder = 1  # indicates how many new suffixes we need to insert

        end = 0  # at the beginning we're looking at word[0:0]

        for end in range(len(word)):  # we iterate through the whole word
            char = word[end]  # the current letter
            if actnode.outedges:
                if actedge is not None:
                    # if there is already an active edge we need to look at this first
                    charindices = actedge.charindices
                    edge_chars = word[charindices]
                    edge_char = edge_chars[actlen]  # letter on edge which is compared with the current char
                    if char == edge_char:
                        # if the current letter fits on the edge we just increase actlen and remainder
                        actlen += 1  # increase active length
                        remainder += 1  # increase remainder

                    else:
                        # if it does not fit anymore create a new edge:
                        new_incices = (actlen, '#')  # new edge goes from actlen to end of string
                        new_parent = actedge
                        newedge = Node(new_incices, new_parent, None, None, None)

                        # the old active edge gets changed:
                        actedge.charindices = (charindices[0], actlen)  # old edge goes only from old start to actlen
                        actedge.outedges.append(newedge)  # the new edge is a child of this node

                        # the active edge needs to be changed, but how??
                        actedge = None #???????
                        actlen -= 1
                        remainder -=1

                else:
                    # if there is no active edge we need to go through all the existing edges and compare them
                    for edge in actnode.outedges:  # go through all the children
                        # if the letter fits increase the remainder and change the active point
                        first_edge_char = word[charindices ]
                        if char ==





