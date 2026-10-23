#!/bin/bash
#SBATCH -p typhon
#SBATCH -N 1
#SBATCH --ntasks=96
#SBATCH --cpus-per-task=1
#SBATCH --job-name=g4test
#SBATCH --time=2:00:00
#SBATCH --output=slurm.out
#SBATCH --mem=200G

#--------------- Compile -----------------
codedir="/home/nianyic/gadget4_development"
cwd=$(pwd)
source $codedir/module_ias.sh
#make clean
#-------- Copy over relevant files --------
outdir="/home/nianyic/scratch1/FMsims/gadget4/2lpt"
cd $cwd

mkdir -p $outdir
cp param-ic.txt $outdir
cp outputs.txt $outdir
cp Gadget4 $outdir
cp $codedir/data/input_spectrum_PLANCK15.txt $outdir
cd $outdir

#------------- Execute --------------------
mpirun -np 96 ./Gadget4  param-ic.txt 6 > log-ic
