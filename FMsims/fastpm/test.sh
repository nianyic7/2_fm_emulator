#!/bin/bash
#SBATCH -p typhon
#SBATCH -N 1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=24
#SBATCH --job-name=test
#SBATCH --time=2:00:00
#SBATCH --output=slurm.out
#SBATCH --mem=100G
#SBATCH --mail-type=ALL
#SBATCH --mail-user=nianyi.chen7@gmail.com

#--------------- Compile -----------------
codedir="/home/nianyic/fastpm"
cwd=$(pwd)
source $codedir/module_ias.sh
#make clean
#cd $codedir
#make clean DIR=$cwd
#make -j 8 DIR=$cwd
#-------- Copy over relevant files --------
outdir="/home/nianyic/scratch1/nbodytest/fastpm"
#cd $cwd

mkdir -p $outdir
#cd $outdir
export OMP_NUM_THREADS=24
#------------- Execute --------------------
mpirun -np 4 $codedir/src/fastpm nbodykit.lua 
