from SuffixTree import SuffixTree
import json
import time
import matplotlib.pylab as plt
import numpy as np


def current_milli_time():
    return round(time.perf_counter() * 1000)

def get_current_time_for_filename():
    return time.strftime("%Y-%m-%d-%H-%M-%S")


# ---------------- Settings ----------------

dataset = "s_1-1_1M.txt"
dataset_path = f"datasets/{dataset}"

number_of_lines = 1000
sequences_length = 76  # all sequences are equally long

save_outputs = True
save_graphs = True

lines_param = f"_lines-{number_of_lines}"
time_param = f"_{get_current_time_for_filename()}"

outputs_path = "outputs/"
unique_sequences_output_path = f"{outputs_path}task3_unique_sequences{lines_param}{time_param}.json"
unique_sequences_most_common_suffixes_output_path = f"{outputs_path}task3_unique_sequences_most_common_suffixes{lines_param}{time_param}.json"
most_common_suffixes_output_path = f"{outputs_path}task3_most_common_suffixes{lines_param}{time_param}.json"
adapter_match_lengths_output_path = f"{outputs_path}task3_adapter_match_lengths{lines_param}{time_param}.json"

graphs_path = "graphs/"
remaining_lengths_distribution_graph_path = f"{graphs_path}task3_remaining_lengths_distribution{lines_param}{time_param}.svg"
unique_sequences_frequency_distribution_graph_path = f"{graphs_path}task3_unique_sequences_frequency_distribution{lines_param}{time_param}.svg"


# ---------------- Compute Suffix Tree ----------------

suffix_tree = SuffixTree()

start_time = current_milli_time()
with open(dataset_path, "r") as file:
    for line_num, line in enumerate(file):
        if line_num >= number_of_lines:
            break
        suffix_tree.add_string(line.strip())
end_time = current_milli_time()

print(f"Time needed to compute Suffix Tree: {end_time - start_time} ms")


# ---------------- Count number of unique sequences ----------------

start_time = current_milli_time()
unique_sequences = suffix_tree.count_unique_sequences()
end_time = current_milli_time()

print(f"\nTime needed to count number of unique sequences: {end_time - start_time} ms")

if save_outputs:
    with open(unique_sequences_output_path, "w") as file:
        json.dump(unique_sequences, file)
else:
    print(unique_sequences[:100])

if save_graphs:
    unique_sequences_frequency_distribution = [c / number_of_lines for c, _ in unique_sequences]

    curr_fig, curr_ax = plt.subplots()
    curr_ax.bar(np.arange(len(unique_sequences)), unique_sequences_frequency_distribution)
    curr_ax.set(title="Task 3: Unique Sequences Frequency Distribution", xlabel="Unique Sequence", ylabel="Occurrence Probability")
    curr_fig.savefig(unique_sequences_frequency_distribution_graph_path)


# ---------------- Find most common suffixes ----------------

start_time = current_milli_time()
most_common_suffixes = suffix_tree.find_most_common_suffixes()
end_time = current_milli_time()

print(f"\nTime needed to find most common suffixes: {end_time - start_time} ms")

if save_outputs:
    with open(most_common_suffixes_output_path, "w") as file:
        json.dump([(count, length, suffix_tree.strings[node.string_id[0]][-length:-1])
                   for count, length, node in most_common_suffixes[:1000]], file)
else:
    print(most_common_suffixes[:1000])


# ---------------- Determine adapter ----------------

# assume most common suffix is adapter
_, length, adapter_leaf_node = most_common_suffixes[0]
adapter = suffix_tree.strings[adapter_leaf_node.string_id[0]][-length:-1]
print(f"\nMost likely adapter sequence: {adapter}")


# ---------------- Find adapter suffix-prefix matches and remaining lengths distribution ----------------

adapter_string_id = suffix_tree.add_string(adapter)

start_time = current_milli_time()
adapter_match_lengths = suffix_tree.find_suffix_matches_for_prefix(adapter_string_id)
end_time = current_milli_time()

print(f"\nTime needed to find adapter prefix-suffix matches: {end_time - start_time} ms")

if save_outputs:
    with open(adapter_match_lengths_output_path, "w") as file:
        json.dump(adapter_match_lengths, file)
else:
    print(adapter_match_lengths)

if save_graphs:
    remaining_lengths = sequences_length - np.asarray(list(adapter_match_lengths.values()))
    remaining_lengths_distribution, _ = np.histogram(remaining_lengths, bins=max(remaining_lengths) + 1, density=True)

    curr_fig, curr_ax = plt.subplots()
    curr_ax.bar(np.arange(len(remaining_lengths_distribution)), remaining_lengths_distribution)
    curr_ax.set(title="Task 3: Remaining Sequence Length Distribution", xlabel="Remaining Sequence Length", ylabel="Occurrence Probability")
    curr_fig.savefig(remaining_lengths_distribution_graph_path)


# ---------------- Find most common suffixes of unique sequences ----------------
del suffix_tree

suffix_tree = SuffixTree()

start_time = current_milli_time()
for _, unique_sequence in unique_sequences:
    suffix_tree.add_string(unique_sequence)
end_time = current_milli_time()

print(f"\nTime needed to compute unique sequence Suffix Tree: {end_time - start_time} ms")

start_time = current_milli_time()
unique_sequences_most_common_suffixes = suffix_tree.find_most_common_suffixes()
end_time = current_milli_time()

print(f"\nTime needed to find most common suffixes in unique sequence Suffix Tree: {end_time - start_time} ms")

if save_outputs:
    with open(unique_sequences_most_common_suffixes_output_path, "w") as file:
        json.dump([(count, length, suffix_tree.strings[node.string_id[0]][-length:-1])
                   for count, length, node in unique_sequences_most_common_suffixes[:1000]], file)
else:
    print(unique_sequences_most_common_suffixes[:1000])
