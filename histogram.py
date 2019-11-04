import json
import time
import matplotlib.pylab as plt
import numpy as np


def get_current_time_for_filename():
    return time.strftime("%Y-%m-%d-%H-%M-%S")


number_of_lines = 1000
max_mismatch_rate = 0.25

lines_param = f"_lines-{number_of_lines}"
mismatch_param = f"_mismatch-rate-{max_mismatch_rate}"
time_param = f"_{get_current_time_for_filename()}"

sequences_length_task1_2 = 50
sequences_length_task3 = 76

graphs_path = "graphs/"
remaining_lengths_distribution_graph_path = f"{graphs_path}task3_remaining_lengths_distribution{lines_param}{time_param}.svg"
task2_graph_path = f"{graphs_path}task2_remaining_lengths_distribution{lines_param}{mismatch_param}{time_param}.svg"

save_graphs = True



# remaining_lengths = sequences_length_task1_2 - np.asarray(list(adapter_match_lengths.values()))
# remaining_lengths_distribution, b1 = np.histogram(remaining_lengths, bins=max(remaining_lengths) + 1, density=True)
#
# curr_fig, curr_ax = plt.subplots()
# curr_ax.bar(np.arange(len(remaining_lengths_distribution)), remaining_lengths_distribution)
# curr_ax.set(title="Task 1: Remaining Sequence Length Distribution", xlabel="Remaining Sequence Length", ylabel="Occurrence Probability")
# if save_graphs:
#     curr_fig.savefig(task1_graph_path)
# else:
#     plt.show()
#
# remaining_lengths = sequences_length_task1_2 - np.asarray(list(adapter_match_lengths_with_mismatches.values()))
# remaining_lengths_distribution, b2 = np.histogram(remaining_lengths, bins=max(remaining_lengths), density=True)
#
# curr_fig, curr_ax = plt.subplots()
# curr_ax.bar(np.arange(len(remaining_lengths_distribution)), remaining_lengths_distribution)
# curr_ax.set(title="Task 2: Remaining Sequence Length Distribution", xlabel="Remaining Sequence Length", ylabel="Occurrence Probability")
# if save_graphs:
#     curr_fig.savefig(task2_graph_path)
# else:
#     plt.show()

with open("outputs/task3_adapter_match_lengths_lines-100000_2019-11-01-18-36-54.json") as f:
    adapter_match_lengths = json.load(f)
remaining_lengths = sequences_length_task3 - np.asarray(list(adapter_match_lengths.values()))
remaining_lengths_distribution, b3 = np.histogram(remaining_lengths, bins=np.arange(sequences_length_task3 + 1), density=True)

curr_fig, curr_ax = plt.subplots()
curr_ax.bar(np.arange(len(remaining_lengths_distribution)), remaining_lengths_distribution)
curr_ax.set(title="Task 3: Remaining Sequence Length Distribution", xlabel="Remaining Sequence Length", ylabel="Occurrence Probability")
if save_graphs:
    curr_fig.savefig(remaining_lengths_distribution_graph_path)
else:
    plt.show()

