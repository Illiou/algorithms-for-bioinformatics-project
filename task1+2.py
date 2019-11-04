from SuffixTree import SuffixTree
import json
import time
import numpy as np
import matplotlib.pyplot as plt


def current_milli_time():
    return round(time.perf_counter() * 1000)

def get_current_time_for_filename():
    return time.strftime("%Y-%m-%d-%H-%M-%S")

# ---------------- Settings ----------------

adapter = "TGGAATTCTCGGGTGCCAAGGAACTCCAGTCACACAGTGATCTCGTATGCCGTCTTCTGCTTG"
dataset = "s_3_sequence_1M.txt"
dataset_path = f"datasets/{dataset}"

number_of_lines = 1000000
sequences_length = 50  # all sequences are equally long
max_mismatch_rate = 0.1

check_correctness_and_print_suffixes = False
save_outputs = False
save_graphs = False

lines_param = f"_lines-{number_of_lines}"
mismatch_param = f"_mismatch-rate-{max_mismatch_rate}"
time_param = f"_{get_current_time_for_filename()}"

outputs_path = "outputs/"
task1_output_path = f"{outputs_path}task1_adapter_match_lengths{lines_param}{time_param}.json"
task2_output_path = f"{outputs_path}task2_adapter_match_lengths{lines_param}{mismatch_param}{time_param}.json"

graphs_path = "graphs/"
task1_graph_path = f"{graphs_path}task1_remaining_lengths_distribution{lines_param}{time_param}.svg"
task2_graph_path = f"{graphs_path}task2_remaining_lengths_distribution{lines_param}{mismatch_param}{time_param}.svg"


# ---------------- Compute Suffix Tree ----------------

suffix_tree = SuffixTree(adapter)
adapter_string_id = 0

start_time = current_milli_time()
with open(dataset_path, "r") as file:
    for line_num, line in enumerate(file):
        #if line_num >= number_of_lines:
        #    break
        suffix_tree.add_string(line.strip())
end_time = current_milli_time()

print(f"Time needed to compute Suffix Tree: {end_time - start_time} ms")


# print(repr(suffix_tree))
# print(suffix_tree)


# ---------------- Task 1 ----------------

start_time = current_milli_time()
adapter_match_lengths = suffix_tree.find_suffix_matches_for_prefix(adapter_string_id)
end_time = current_milli_time()
time_needed.append(end_time - start_time)

print(f"\nTime needed to find adapter matches: {end_time - start_time} ms")
print(f"Number of matched sequences: {sum(v > 0 for v in adapter_match_lengths.values())}")


if check_correctness_and_print_suffixes:
    matched_suffixes = []
    for string_id, match_length in adapter_match_lengths.items():
        matched_suffixes.append(adapter[:match_length])
        # correctness testing
        if adapter[:match_length] != suffix_tree.strings[string_id][-match_length - 1:-1]:
            print(f"Something went wrong at string {string_id} with match length {match_length}")
            print(f"Adapter part: {adapter[:match_length]}   string part: {suffix_tree.strings[string_id][-match_length - 1:-1]}")
    print(matched_suffixes)

if save_outputs:
    with open(task1_output_path, "w") as file:
        json.dump(adapter_match_lengths, file)

if save_graphs:
    remaining_lengths = sequences_length - np.asarray(list(adapter_match_lengths.values()))
    remaining_lengths_distribution, _ = np.histogram(remaining_lengths, bins=max(remaining_lengths) + 1, density=True)

    curr_fig, curr_ax = plt.subplots()
    curr_ax.bar(np.arange(len(remaining_lengths_distribution)), remaining_lengths_distribution)
    curr_ax.set(title="Task 1: Remaining Sequence Length Distribution", xlabel="Remaining Sequence Length", ylabel="Occurrence Probability")
    curr_fig.savefig(task1_graph_path)


# ---------------- Task 2 ----------------

start_time = current_milli_time()
adapter_match_lengths_with_mismatches = suffix_tree.find_suffix_matches_for_prefix_with_mismatches(adapter_string_id, max_mismatch_rate)
end_time = current_milli_time()


print(f"\nTime needed to find adapter matches with mismatches: {end_time - start_time} ms")
print(f"Number of matched sequences: {sum(v > 0 for v in adapter_match_lengths_with_mismatches.values())}")

if check_correctness_and_print_suffixes:
    matched_suffixes = []
    for string_id, match_length in adapter_match_lengths_with_mismatches.items():
        matched_suffix = suffix_tree.strings[string_id][-match_length - 1:-1]
        matched_suffixes.append(matched_suffix)
        # correctness testing
        actual_mismatches = sum(adapter[i] != matched_suffix[i] for i in range(match_length))
        if match_length > 0 and actual_mismatches / match_length > max_mismatch_rate:
            print(f"Something went wrong at string {string_id} with match length {match_length}. Mismatches {actual_mismatches}/Mismatch Rate {actual_mismatches / match_length}")
            print(f"Adapter part: {adapter[:match_length]}   string part: {suffix_tree.strings[string_id][-match_length - 1:-1]}")
            print(adapter, suffix_tree.strings[string_id])
    print(matched_suffixes)

if save_outputs:
    with open(task2_output_path, "w") as file:
        json.dump(adapter_match_lengths_with_mismatches, file)

if save_graphs:
    remaining_lengths = sequences_length - np.asarray(list(adapter_match_lengths_with_mismatches.values()))
    remaining_lengths_distribution, _ = np.histogram(remaining_lengths, bins=max(remaining_lengths) + 1, density=True)

    curr_fig, curr_ax = plt.subplots()
    curr_ax.bar(np.arange(len(remaining_lengths_distribution)), remaining_lengths_distribution)
    curr_ax.set(title="Task 2: Remaining Sequence Length Distribution", xlabel="Remaining Sequence Length", ylabel="Occurrence Probability")
    curr_fig.savefig(task2_graph_path)
