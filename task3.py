from SuffixTree import SuffixTree
import matplotlib.pylab as plt
import time
import numpy as np

def current_milli_time():
    return round(time.perf_counter() * 1000)

data = 'datasets/s_1-1_1M.txt'

# Running Time Analysis:
time_needed = []
number_of_lines = [1,100,200,300,400,500]
for number in number_of_lines:
    # Construction of tree
    start_time = current_milli_time()
    suffix_tree = SuffixTree('', construction_method="naive", track_terminal_edges=True)
    with open(data,'r') as file:
        for line_num, line in enumerate(file):
            if line_num >= number:
                break
            suffix_tree.add_string(line.strip())

    # finding the adaptersequence:
    start_time = current_milli_time()
    adapter = suffix_tree.most_common_adaptersequence()
    end_time = current_milli_time()
    time_needed.append(end_time-start_time)

plt.plot(number_of_lines, time_needed)
plt.xlabel('Number of Sequences')
plt.ylabel('Runtime in ms')
plt.grid()
plt.savefig('Runtime_task3.pdf')
plt.close()

# Actual task
number_of_lines = 1e3  # 10687775
data = 'datasets/s_1-1_1M.txt'
# Construction of tree
start_time = current_milli_time()
suffix_tree = SuffixTree('', construction_method="naive", track_terminal_edges=True)
with open(data, 'r') as file:
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
len_sequences = []
for string_id, match_length in adapter_match_lengths.items():
    if len(suffix_tree.strings[string_id][:-match_length]) > 0:
        sequences_without_adapter.append(suffix_tree.strings[string_id][:-match_length])
        len_sequences.append(len(suffix_tree.strings[string_id][:-match_length]))
length_distribution = {x: len_sequences.count(x) for x in len_sequences}
lists = sorted(length_distribution.items())  # sorted by key, return a list of tuples
x, y = zip(*lists)  # unpack a list of pairs into two tuples
plt.plot(x, y)
plt.xlabel('Length')
plt.ylabel('Frequency')
plt.grid()
plt.savefig('length_distribution_task3.pdf')
plt.close()

# get number of unique sequences:
suffix_tree = SuffixTree(sequences_without_adapter[0], construction_method="naive", track_terminal_edges=True)
for sequence in sequences_without_adapter[1:]:
    suffix_tree.add_string(sequence)
unique_sequences = suffix_tree.count_unique_sequences()
sorted_unique_sequences = [(k, unique_sequences[k]) for k in sorted(unique_sequences, key=unique_sequences.get, reverse=True)]
for i in range(5):
    print(sorted_unique_sequences[i])
