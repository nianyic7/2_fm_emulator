import numpy as np
import random
import os
# List of i values
i_list = np.arange(0, 5000)
# read in list of seed from seeds.txt
seedlist = []
with open("seeds.txt", "r") as f:
    for line in f:
        tokens = line.strip().split()
        if len(tokens) == 2:
            i, seed = int(tokens[0]), int(tokens[1])
            seedlist.append(seed)
print(f"Read {len(i_list)} seeds from seeds.txt")

# Read template
with open("param_template.txt", "r") as f:
    template = f.read()

# Output files will go in this directory
output_dir = "/home/nianyic/scratch1/FMsims/L400_n128_s40"

seed_pairs = []
rng = np.random.default_rng(seed=42)
for i in i_list:
    run_name = f"run-{i:04d}"
    os.makedirs(f"{output_dir}/{run_name}", exist_ok=True)
    # fixed seed for reproducibility
    # seed = rng.integers(0, 2**30 - 1)
    filled = template.replace("**seed**", str(seed))
    output_path = os.path.join(output_dir, f"{run_name}/param.txt")
    seed = seedlist[i]
    seed_pairs.append((i, seed))
    with open(output_path, "w") as f:
        f.write(filled)
    print(f"Wrote {output_path}")

# Write i-seed pairs to seeds.txt
#print("Writing seeds to:", os.path.abspath("seeds.txt"))
#with open("seeds.txt", "w") as f:
#    for i, seed in seed_pairs:
#        f.write(f"{i}\t{seed}\n")

print("Saved all seeds to seeds.txt")
