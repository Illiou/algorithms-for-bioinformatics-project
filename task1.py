from SuffixTree import SuffixTree
import time

def current_milli_time():
    return round(time.perf_counter() * 1000)

adapter = "TGGAATTCTCGGGTGCCAAGGAACTCCAGTCACACAGTGATCTCGTATGCCGTCTTCTGCTTG"
dataset = "s_3_sequence_1M.txt"
dataset_path = f"datasets/{dataset}"

number_of_lines = 1000

suffix_tree = SuffixTree(adapter, construction_method="naive", track_terminal_edges=True)
adapter_string_id = 0

start_time = current_milli_time()
with open(dataset_path, "r") as file:
    for line_num, line in enumerate(file):
        if line_num >= number_of_lines:
            break
        suffix_tree.add_string(line.strip())

end_time = current_milli_time()
print(f"Time needed: {end_time - start_time} ms")

# print(repr(suffix_tree))
# print(suffix_tree)

adapter_match_lengths = suffix_tree.find_suffix_matches_for_prefix(adapter_string_id)
print(adapter_match_lengths)

matched_suffixes = []
for string_id, match_length in adapter_match_lengths.items():
    matched_suffixes.append(adapter[:match_length])
    if matched_suffixes[-1] != suffix_tree.strings[string_id][-match_length - 1:-1]:
        print(f"Something went wrong at string {string_id} with match length {match_length}")
        print(f"Adapter part: {matched_suffixes[-1]}   string part: {suffix_tree.strings[string_id][-match_length - 1:-1]}")
print(matched_suffixes)


import numpy as np
adapter_match_lengths_values = list(adapter_match_lengths.values())
length_distribution, _ = np.histogram(adapter_match_lengths_values, bins=max(adapter_match_lengths_values), density=True)

import matplotlib.pyplot as plt

curr_fig, curr_ax = plt.subplots()
curr_ax.bar(np.arange(len(length_distribution)), length_distribution)
curr_ax.set(title="Adapter Prefix Length Distribution", xlabel="Adapter Prefix Length", ylabel="Occurrence Probability")
plt.show()
