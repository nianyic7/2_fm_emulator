#!/bin/bash
#SBATCH -p RM
#SBATCH -N 4
#SBATCH --ntasks=256
#SBATCH --cpus-per-task=2
#SBATCH --job-name=zparent
#SBATCH --time=4:00:00
#SBATCH --output=slurm3.out
#SBATCH --mem=200G
#SBATCH --mail-type=END
#SBATCH --mail-user=nianyic@andrew.cmu.edu
#SBATCH --dependency=afterok:24267171
#--------------- Compile -----------------
codedir="/jet/home/nianyic/gadget4_development"
cwd=$(pwd)
source $codedir/load_modules.sh
#make clean
#cd $codedir
#make clean DIR=$cwd
#make -j 8 DIR=$cwd
#-------- Copy over relevant files --------
outdir="/jet/home/nianyic/scratch1/zoom/testrun/parent"
cd $cwd

mkdir -p $outdir
cp param.txt $outdir
cp Gadget4 $outdir
cp outputs.txt $outdir
#cp $codedir/data/input_spectrum_PLANCK15.txt $outdir
cd $outdir

#------------- Execute --------------------
mpirun -np 256 ./Gadget4  param.txt 1 > log3
