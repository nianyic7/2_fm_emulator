#!/bin/bash
#SBATCH -p typhon
#SBATCH -N 1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --job-name=mesh-000
#SBATCH --time=30:00:00
#SBATCH --output=slurm-%x.out
#SBATCH --mem=10G

source ~/.bashrc
conda init
conda activate nbodykit-env
n1=0
n2=200
for ((i=n1; i<n2; i++)); do 
	printf "Running run-%04d\n" $i 
	runname=run-$(printf "%04d" $i) 
	root="/home/nianyic/scratch1/FMsims/L400_n128_s40" 
	#------------- Execute -------------------- 
	srun python create_delta_deltadot_mesh.py --root $root --Lbox 400. --Nmesh 128 --runname $runname
       	sleep 2
done
echo "Done!"
