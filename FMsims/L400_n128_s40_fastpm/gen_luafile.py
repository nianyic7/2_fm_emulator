import numpy as np
import random
import os
# List of i values
i_list = np.arange(0, 5000)

# Read template
with open("template.lua", "r") as f:
    template = f.read()

# Output files will go in this directory
output_dir = "paramfile"


os.makedirs(output_dir, exist_ok=True)
seed_pairs = []
rng = np.random.default_rng(seed=42)
for i in i_list:
    run_name = f"s-{i:04d}"
    # fixed seed for reproducibility
    seed = rng.integers(0, 2**30 - 1)
    filled = template.replace("**run**", run_name).replace("**seed**", str(seed))

    output_path = os.path.join(output_dir, f"{run_name}.lua")
    seed_pairs.append((i, seed))
    with open(output_path, "w") as f:
        f.write(filled)

    print(f"Wrote {output_path}")

# Write i-seed pairs to seeds.txt
print("Writing seeds to:", os.path.abspath("seeds.txt"))
with open("seeds.txt", "w") as f:
    for i, seed in seed_pairs:
        f.write(f"{i}\t{seed}\n")

print("Saved all seeds to seeds.txt")