#!/bin/bash
#SBATCH -p typhon
#SBATCH -N 1
#SBATCH --ntasks=96
#SBATCH --cpus-per-task=1
#SBATCH --job-name=g4test
#SBATCH --time=2:00:00
#SBATCH --output=slurm-%x.out
#SBATCH --mem=200G

#--------------- Compile -----------------
codedir="/home/nianyic/gadget4_development"
cwd=$(pwd)
source $codedir/module_ias.sh
#make clean
#-------- Copy over relevant files --------
run=0000
outdir="/home/nianyic/scratch1/FMsims/L400_n128_s40/run-$run"

cd $outdir

#------------- Execute --------------------
mpirun -np 96 $cwd/Gadget4 param.txt > log
