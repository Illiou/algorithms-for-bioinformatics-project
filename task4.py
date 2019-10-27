from SuffixTree import SuffixTree

import matplotlib.pylab as plt
#from time import time
#import numpy as np


st = SuffixTree("accabbb", construction_method="naive", track_terminal_edges=True)
st.add_string("ccgabbb")
st.add_string('cccabbb')
st.add_string('bccccd')
st.add_string('stcccd')
#st.add_string(('ababab'))
#st.add_string("ATA")
#st.add_string("TB")
suffix = st.find_barcodes()
print(st)