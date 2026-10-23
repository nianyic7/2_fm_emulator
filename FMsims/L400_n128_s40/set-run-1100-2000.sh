#!/bin/bash

# Generate simulation run scripts for runs 1100-1999
template="run-template.sh"

for n1 in $(seq 1100 100 1900); do
    n2=$((n1 + 100))
    jobname="r${n1}"
    outfile="run-${n1}.sh"

    sed -e "s/^#SBATCH --job-name=.*/#SBATCH --job-name=${jobname}/" \
        -e "s/^n1=.*/n1=${n1}/" \
        -e "s/^n2=.*/n2=${n2}/" \
        "$template" > "$outfile"

    chmod +x "$outfile"
    echo "Created $outfile (n1=${n1}, n2=${n2}, job-name=${jobname})"
done

# Generate mesh post-processing scripts for runs 1100-1999
mesh_template="template_mesh.sh"

for n1 in $(seq 1100 200 1900); do
    n2=$((n1 + 200))
    if [ $n2 -gt 2000 ]; then
        n2=2000
    fi
    jobname="mesh-${n1}"
    outfile="genmesh-${n1}.sh"

    sed -e "s/^#SBATCH --job-name=.*/#SBATCH --job-name=${jobname}/" \
        -e "s/^n1=.*/n1=${n1}/" \
        -e "s/^n2=.*/n2=${n2}/" \
        "$mesh_template" > "$outfile"

    chmod +x "$outfile"
    echo "Created $outfile (n1=${n1}, n2=${n2}, job-name=${jobname})"
done
