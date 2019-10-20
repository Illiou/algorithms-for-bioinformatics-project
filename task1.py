def set_terminal_labels(self):
    to_be_processed = [n for n in self.root.edges.values()]
    while len(to_be_processed) > 0:
        node = to_be_processed.pop()
        for n in node.edges.values():
            if n.edges:
                to_be_processed.append(n)
            else:
                string = self.strings[node.string_id]
                if string[node.start] == '$':
                    node.l_v.append(n.string_id)