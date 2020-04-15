#!/bin/bash -x
#SBATCH -J policySimus # A single job name for the array
#SBATCH -n 4                # Number of cores
#SBATCH -N 1                # Ensure that all cores are on one machine
#SBATCH -p shared
#SBATCH -t 00:15:00         # Runtime in D-HH:MM:SS, minimum of 10 minutes
#SBATCH --mem=40000          # Memory pool for all cores (see also --mem-per-cpu) MBs
#SBATCH -o %J.out  # File to which STDOUT will be written, %j inserts jobid
#SBATCH -e %J.err  # File to which STDERR will be written, %j inserts jobid

set -x

date
cdir=$(pwd)
#mkdir -p $tempdir
#cd $tempdir


#module load python/3.6.3-fasrc01
python3 run_simulation.py $1 ${SLURM_ARRAY_TASK_ID} 
