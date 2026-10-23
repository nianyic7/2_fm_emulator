#!/bin/bash
#SBATCH -p typhon
#SBATCH -N 1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=24
#SBATCH --job-name=mptest
#SBATCH --time=2:00:00
#SBATCH --output=slurm.out
#SBATCH --mem=100G

#--------------- Compile -----------------
codedir="/home/nianyic/MP-Gadget"
cwd=$(pwd)
source $codedir/module_ias.sh
#make clean
#-------- Copy over relevant files --------
outdir="/home/nianyic/scratch1/FMsims/mpgadget"

mkdir -p $outdir
cp paramfile.gadget $outdir
cd $outdir
export OMP_NUM_THREADS=24
#------------- Execute --------------------
mpirun -np 4 $codedir/gadget/MP-Gadget  paramfile.gadget > log
