#!/bin/bash
#SBATCH -p typhon
#SBATCH -N 1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=96
#SBATCH --job-name=test
#SBATCH --time=72:00:00
#SBATCH --output=slurm-p2m.out
#SBATCH --mem=100G

#--------------- Compile -----------------
codedir="/home/nianyic/fastpm"
cwd=$(pwd)
source $codedir/module_ias.sh
#-------- Copy over relevant files --------
oroot="/home/nianyic/scratch1/FMsims/L400_n128_s40"

n1=0
n2=100

N_CORES=96

source ~/.bashrc
conda activate nbodykit-env 

for ((i=n1; i<n2; i++)); do

	runname=s-$(printf "%04d" $i)
        outdir=$oroot/$runname

	python part2mesh.py --rundir $outdir --Nmesh 128 --Lbox 400. --downsample 2 &
	pid=$!
	echo "PID $pid param $i"
	taskset -cp $pid       # Allowed CPUs
	ps -o pid,psr,cmd -p $pid  # Current CPU

	if (( (i+1) % N_CORES == 0 )); then
        	wait
    	fi
done

