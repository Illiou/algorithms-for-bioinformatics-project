from SuffixTree import SuffixTree
from SuffixGrapher import Grapher
import matplotlib.pylab as plt

"""
st = SuffixTree()
st.add_string("TAAC")
st.add_string("ACT")
st.set_terminal_labels()
match = st.suffix_prefix_match()
print(match)
g = Grapher(st)
g.createGraphviz()
"""

#Info for second task
adaptersequence = "TGGAATTCTCGGGTGCCAAGGAACTCCAGTCACACAGTGATCTCGTATGCCGTCTTCTGCTTG"
filename = "datasets/s_3_sequence_1M.txt"
number_of_matches = 0
length_distribution = {}

i = 0
with open(filename, "r") as infile:
    for line in infile:
        line = line.strip()
        st = SuffixTree()
        st.add_string(line)
        st.add_string(adaptersequence)
        st.set_terminal_labels()
        length_match = st.suffix_prefix_match()

        if length_match > 0:
            number_of_matches += 1
            length_rest = len(line) - length_match
            if length_rest in length_distribution:
                length_distribution[length_rest] += 1
            else:
                length_distribution[length_rest] = 1
        i+=1
        if i % 10000 == 0:
            print i

lists = sorted(length_distribution.items()) # sorted by key, return a list of tuples

x, y = zip(*lists) # unpack a list of pairs into two tuples
value = [float(element)/i*100 for element in y]
xlist = [element for element in x]
plt.plot(xlist, value)
plt.xlabel('Remaining Length')
plt.ylabel('Amount of Sequences [%]')
plt.grid()
plt.savefig('task1.pdf')