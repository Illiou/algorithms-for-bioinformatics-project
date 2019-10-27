from SuffixTree import SuffixTree

#import matplotlib.pylab as plt
#from time import time
#import numpy as np


st = SuffixTree("acc", construction_method="naive", track_terminal_edges=True)
st.add_string("ccg")
st.add_string('ccc')
st.add_string('abbcg')
st.add_string('abbccc')
#st.add_string("ATA")
#st.add_string("TB")
suffix = st.most_common_adaptersequence()
print(suffix)
"""
print(st)
for leave in st.leaves:
    if isinstance(leave.string_id, list):
        string = st.strings[leave.string_id[0]][leave.start:leave.end]
    else:
        string = st.strings[leave.string_id][leave.start:leave.end]
    print(string)
"""