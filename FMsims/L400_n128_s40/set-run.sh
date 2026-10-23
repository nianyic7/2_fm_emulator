#!/bin/bash

# template file
template="run-template.sh"

# loop over desired jobs
for n1 in $(seq 100 100 1000); do
    n2=$((n1 + 100))
    jobname="r${n1}"
    outfile="run-${n1}.sh"

    # copy template and substitute values
    sed -e "s/^#SBATCH --job-name=.*/#SBATCH --job-name=${jobname}/" \
        -e "s/^n1=.*/n1=${n1}/" \
        -e "s/^n2=.*/n2=${n2}/" \
        "$template" > "$outfile"

    chmod +x "$outfile"
    echo "Created $outfile (n1=${n1}, n2=${n2}, job-name=${jobname})"
done
