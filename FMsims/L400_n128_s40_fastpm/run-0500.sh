#!/bin/bash
#SBATCH -p typhon
#SBATCH -N 1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=24
#SBATCH --job-name=test
#SBATCH --time=72:00:00
#SBATCH --output=slurm.out
#SBATCH --mem=100G

#--------------- Compile -----------------
codedir="/home/nianyic/fastpm"
cwd=$(pwd)
source $codedir/module_ias.sh
#-------- Copy over relevant files --------
oroot="/home/nianyic/scratch1/FMsims/L400_n128_s40"

n1=0
n2=500

export OMP_NUM_THREADS=24

for ((i=n1; i<n2; i++)); do
	printf "Running paramfile: paramfile/s-%04d.lua\n" $i

	runname=s-$(printf "%04d" $i)
        outdir=$oroot/$runname
	mkdir -p $outdir
	cp $cwd/paramfile/$runname.lua $outdir
	cd $outdir

	mpirun -np 4 $codedir/src/fastpm $runname.lua >log
	sleep 4
done

