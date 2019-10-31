from SuffixTree import SuffixTree
import matplotlib.pylab as plt
import time


def current_milli_time():
    return round(time.perf_counter() * 1000)

data = 'datasets/s_1-1_1M.txt'

# Running Time Analysis:
time_needed = []
number_of_lines = [1,100,200,400,800,1600,3200,6400]
for number in number_of_lines:
    # Construction of tree
    start_time = current_milli_time()
    suffix_tree = SuffixTree(track_terminal_edges=True)
    with open(data,'r') as file:
        for line_num, line in enumerate(file):
            if line_num >= number:
                break
            suffix_tree.add_string(line.strip())
    end_time = current_milli_time()

    print(f"Time needed to compute Suffix Tree: {end_time - start_time} ms with {number} lines")

    # finding the adaptersequence:
    start_time = current_milli_time()
    adapter = suffix_tree.find_most_common_suffixes()
    end_time = current_milli_time()
    time_needed.append(end_time-start_time)

plt.plot(number_of_lines, time_needed)
plt.xlabel('Number of Sequences')
plt.ylabel('Runtime in ms')
plt.grid()
plt.show()
