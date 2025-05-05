import matplotlib.pyplot as plt
import math
import glob
import numpy as np

# -------------------------- Utility Functions -------------------------- #

def getindex(hexa, ttl_lines, w):
    dec = int(hexa, 16)
    add = format(dec, '032b')
    tag = 32 - int(math.log2(ttl_lines)) - int(math.log2(w)) - 2
    return int(add[tag:tag+8], 2)

def gettag(hexa, ttl_lines, w):
    dec = int(hexa, 16)
    add = format(dec, '032b')
    tag = 32 - int(math.log2(ttl_lines)) - int(math.log2(w)) - 2
    return int(add[:tag], 2)

def getoffset(hexa, ttl_lines, w):
    dec = int(hexa, 16)
    add = format(dec, '032b')
    offset = int(math.log2(w)) + 2
    return format(int(add[32 - offset:32], 2), '032b')

def create_cache_data(w, ttl_lines):
    return [[[ -1 for _ in range(4)] for _ in range(w)] for _ in range(ttl_lines)]

# -------------------------- Main Processing ---------------------------- #

def process_trace_file(file_name, memory, words_per_line, total_lines, output_file):
    hit_ratios = []
    hit_trace = {}

    for w in words_per_line:
        with open(file_name, "r") as f:
            instructions = f.readlines()

        output_file.write(f'FILE: {file_name} words per line: {w}\n\n')

        cache_valid = [False] * total_lines
        cache_tags = [-1] * total_lines
        cache_data = create_cache_data(w, total_lines)

        hits = 0
        hit_progression = []

        for c, line in enumerate(instructions, 1):
            parts = line.strip().split()
            if len(parts) < 3:
                continue

            op, addr_hex, value = parts[0], parts[1][2:], parts[2]
            index = getindex(addr_hex, total_lines, w)
            tag = gettag(addr_hex, total_lines, w)
            offset_bin = getoffset(addr_hex, total_lines, w)

            block_bits = int(math.log2(w)) if w > 1 else 0
            block_offset = int(offset_bin[:block_bits], 2) if block_bits > 0 else 0
            byte_offset = int(offset_bin[-2:], 2)

            address = int(addr_hex, 16)

            # Write to memory and cache
            if op == 's':
                memory[address % 10**6] = value
                cache_data[index][block_offset][byte_offset] = value

            # Address alignment for block fill
            aligned_addr = addr_hex[:30 - int(math.log2(w))] + '0' * (int(math.log2(w)) + 2)
            aligned_hex = int(aligned_addr, 16)

            if cache_valid[index] and cache_tags[index] == tag:
                hits += 1
                data = cache_data[index][block_offset][byte_offset]
                msg = f'cache hit! {"read" if op == "l" else "already in"} cache: {tag} {index} {block_offset} {byte_offset} {data}\n'
            else:
                # Cache miss
                cache_valid[index] = True
                cache_tags[index] = tag
                for i in range(w):
                    for j in range(4):
                        mem_index = (aligned_hex + (i * 4) + j) % 10**6
                        cache_data[index][i][j] = memory[mem_index]
                data = cache_data[index][block_offset][byte_offset]
                msg = f'cache miss! {"read" if op == "l" else "stored"}: {tag} {index} {block_offset} {byte_offset} {data}\n'

            output_file.write(msg)
            hit_progression.append(hits * 100 / c)

        hit_ratios.append(hits * 100 / len(instructions))
        hit_trace[w] = hit_progression

    return hit_ratios, hit_trace

# -------------------------- Main Script -------------------------------- #

def main():
    total_lines = 256
    words_per_line = np.array([1, 2, 4, 8, 16])
    trace_files = glob.glob("*.trace")
    hit_ratio_variation = {}
    hit_progress = {}

    with open("memory.dat", "r") as m:
        memory = m.readlines()

    with open("output.txt", "w") as out:
        for trace in trace_files:
            ratios, trace_hits = process_trace_file(trace, memory.copy(), words_per_line, total_lines, out)
            hit_ratio_variation[trace] = ratios
            hit_progress[trace] = trace_hits[16]  # Only store 16-word progression

    # Plot hit ratio vs. log2(words per line)
    for trace, ratios in hit_ratio_variation.items():
        plt.plot(np.log2(words_per_line), ratios, label=trace)
    plt.title("Hit Rate vs log2(Words per Line)")
    plt.xlabel("log2(Words per Line)")
    plt.ylabel("Hit Rate (%)")
    plt.legend(loc="lower right")
    plt.savefig("hit_ratio_wp.png")
    plt.show()

    # Plot hit ratio vs instruction count for 16-word cache
    for trace, progression in hit_progress.items():
        plt.plot(range(len(progression)), progression, label=trace)
    plt.title("Hit Rate vs Instruction Count [16 Words per Line]")
    plt.xlabel("Instruction Count")
    plt.ylabel("Hit Rate (%)")
    plt.xlim(0, min(8e5, len(progression)))
    plt.legend(loc="lower right")
    plt.savefig("hit_ratio_ni.png")
    plt.show()

if __name__ == "__main__":
    main()
