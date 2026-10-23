#!/bin/bash
#SBATCH -p typhon
#SBATCH -N 1
#SBATCH --ntasks=96
#SBATCH --cpus-per-task=1
#SBATCH --job-name=r400
#SBATCH --time=30:00:00
#SBATCH --output=slurm-%x.out
#SBATCH --mem=200G
#--------------- Compile -----------------
codedir="/home/nianyic/gadget4_development"
cwd=$(pwd)
source $codedir/module_ias.sh
#make clean 
#-------- Copy over relevant files --------
n1=400
n2=500
for ((i=n1; i<n2; i++)); do 
	printf "Running run-%04d\n" $i 
	runname=run-$(printf "%04d" $i) 
	outdir="/home/nianyic/scratch1/FMsims/L400_n128_s40/$runname" 
	cp ewald_table_1-1-1_64-64-64_precision8-order3.dat $outdir 
	cd $outdir 
	#------------- Execute -------------------- 
	mpirun -np 96 $cwd/Gadget4 param.txt > log
       	sleep 2
done
echo "Done!"
