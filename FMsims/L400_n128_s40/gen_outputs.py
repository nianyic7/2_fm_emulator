import numpy as np
import random
import os
# List of i values


#def da(a, da0=0.012):
#    da = da0 * np.power(a, 0.2)
#    return da

def da(a, da0=0.01):
    da = da0 * np.power(a, 0.5)
    return da

def is_valid_sample(xlist):
    dloga = np.abs(np.diff(np.log(xlist)))
    if np.any(dloga < 0.008):
        return False
    return True

def sample_triplets(n=20, a0=0.0111, a1=0.99, max_tries=30000):
    for _ in range(max_tries):
        x = np.sort(np.random.uniform(a0, a1, n))
        dx = da(x)
        x_left = x - dx
        x_right = x + dx
        # create array with [x0_left, x0, x0_right, x1_left, x1, x1_right, ...]
        x_triplet = np.column_stack((x_left, x, x_right)).flatten()
        indsorted = np.argsort(x_triplet)
        reverse_ind = np.argsort(indsorted)
        x_triplet_sorted = x_triplet[indsorted]
        # Check if the triplets are non-overlapping
        if is_valid_sample(x_triplet_sorted):
            return x_triplet_sorted, reverse_ind, x

    raise RuntimeError("Failed to sample non-overlapping triplets after many tries.")

def write_triplets_to_file(filename1, filename_ind, data, reverse_ind):
    # write data to file, one number per line
    with open(filename1, 'w') as f:
        for value in data:
            f.write(f"{value:.6f}\n")
    # write reverse indices to another file
    with open(filename_ind, 'w') as f:
        for value in reverse_ind:
            f.write(f"{value}\n")
    print(f"Wrote {filename1} and {filename_ind}")

        
if __name__ == "__main__":
    i_list = np.arange(0, 5000)
    np.random.seed(73837) 
    odir = "/home/nianyic/scratch1/FMsims/L400_n128_s40"
    midpoint_list = []
    for i in i_list:
        run_name = f"run-{i:04d}"
        os.makedirs(f"{odir}/{run_name}", exist_ok=True)
        filename = f"{odir}/{run_name}/outputs.txt"
        file_ind = f"{odir}/{run_name}/reverse_index.txt"
        # Sample triplets
        x_triplet_sorted, reverse_ind, x = sample_triplets()
        # Write triplets to files
        write_triplets_to_file(filename, file_ind, x_triplet_sorted, reverse_ind)
        midpoint_list.append(x)
        print(f"Wrote {filename}")
    # Save the midpoint list to a file
    midpoint_file = "all_avalues.txt"
    with open(midpoint_file, 'w') as f:
        for mid in midpoint_list:
            f.write(" ".join(f"{val:.6f}" for val in mid) + "\n")
    print(f"Saved all midpoints to {midpoint_file}")
