from SuffixTree import SuffixTree
from SuffixGrapher import Grapher
import matplotlib.pylab as plt
from time import time
import numpy as np


st = SuffixTree()
st.add_string("TAAC")
st.add_string("ACT")
st.set_terminal_labels()
match = st.suffix_prefix_match()
print(match)
g = Grapher(st)
g.createGraphviz()
