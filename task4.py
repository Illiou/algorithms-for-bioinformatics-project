from SuffixTree import SuffixTree
import csv
import matplotlib.pylab as plt
import time
import numpy as np

def current_milli_time():
    return round(time.perf_counter() * 1000)

number_of_lines = 1e3  # 10687775
data = 'datasets/MultiplexedSamples'

# Construction of tree
start_time = current_milli_time()
suffix_tree = SuffixTree('', construction_method="naive", track_terminal_edges=True)
with open(data,'r') as file:
    for line_num, line in enumerate(file):
        if line_num >= number_of_lines:
            break
        suffix_tree.add_string(line.strip())
end_time = current_milli_time()
print(f"Time needed for construction of tree: {end_time - start_time} ms")

# finding the adaptersequence:
start_time = current_milli_time()
adapter = suffix_tree.most_common_adaptersequence()
end_time = current_milli_time()
print(f"Time needed for finding the adaptersequence: {end_time - start_time} ms")
print('Adapter found: ', adapter)

# remove the adapter from the sequences:
suffix_tree = SuffixTree(adapter, construction_method="naive", track_terminal_edges=True)
with open(data, "r") as file:
    for line_num, line in enumerate(file):
        if line_num >= number_of_lines:
            break
        suffix_tree.add_string(line.strip())

adapter_string_id = 0
adapter_match_lengths = suffix_tree.find_suffix_matches_for_prefix(adapter_string_id)

sequences_without_adapter = []
for string_id, match_length in adapter_match_lengths.items():
    if len(suffix_tree.strings[string_id][:-match_length]) > 0:
        sequences_without_adapter.append(suffix_tree.strings[string_id][:-match_length])

# find barcodes:
start_time = current_milli_time()
suffix_tree = SuffixTree(sequences_without_adapter[0], construction_method="naive", track_terminal_edges=True)
for sequence in sequences_without_adapter[1:]:
    suffix_tree.add_string(sequence)

barcodes, sequences_per_sample, number_sequences_per_sample, length_of_sequences = suffix_tree.find_barcodes()
end_time = current_milli_time()
print(f"Time needed for finding the barcodes: {end_time - start_time} ms")
print(barcodes, number_sequences_per_sample)

# save to file:
w = csv.writer(open("number_sequences_per_sample.csv", "w"))
for key, val in number_sequences_per_sample.items():
    w.writerow([key, val])

t = csv.writer(open("sequences_per_sample.csv", "w"))
for key, val in sequences_per_sample.items():
    w.writerow([key, val])

k = csv.writer(open("length_of_sequences.csv", "w"))
for key, val in length_of_sequences.items():
    k.writerow([key, val])

for barcode in length_of_sequences.keys():
    length_distribution = {x: length_of_sequences[barcode].count(x) for x in length_of_sequences[barcode]}
    lists = sorted(length_distribution.items())  # sorted by key, return a list of tuples
    x, y = zip(*lists)  # unpack a list of pairs into two tuples
    plt.plot(x, y, label=barcode)
plt.legend()
plt.xlabel('Length')
plt.ylabel('Frequency')
plt.grid()
plt.savefig('length_distribution_task4.pdf')
plt.close()

# most frequently occuring sequence within each sample:






