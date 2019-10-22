from SuffixTree import SuffixTree
from SuffixGrapher import Grapher
import matplotlib.pylab as plt
from time import time
import numpy as np

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

length_distribution = {}
time_needed = []
number = [1] #, 2, 5, 10, 50, 100, 500, 1000, 5000, 10000, 20000, 50000, 100000
i = 0
for k in number:
    print k
    with open(filename, "r") as infile:
        number_of_matches = 0
        start = time()
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
            #if i == k:
            #   break
        end = time()
        time_needed.append(end - start)

#np.savetxt('Number', number)
#np.savetxt('time', time_needed)

print number_of_matches

"""
plt.plot(number, time_needed)
plt.xlabel("Number of Sequences")
plt.ylabel("Time needed [s]")
plt.grid()
plt.show()
plt.savefig("task1_runtime.pdf")

lists = sorted(length_distribution.items()) # sorted by key, return a list of tuples

x, y = zip(*lists) # unpack a list of pairs into two tuples
value = [float(element)/i*100 for element in y]
xlist = [element for element in x]
plt.plot(xlist, value)
plt.xlabel('Remaining Length')
plt.ylabel('Amount of Sequences [%]')
plt.grid()
plt.savefig('task1.pdf')
"""