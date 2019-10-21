from SuffixTree import SuffixTree
from SuffixGrapher import Grapher

st = SuffixTree()
st.add_string("TAATCG")
st.add_string("CGAAT")
st.set_terminal_labels()
match = st.suffix_prefix_match(0,1)
print(match)
g = Grapher(st)
g.createGraphviz()