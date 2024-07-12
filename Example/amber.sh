#!/bin/bash
#SBATCH --time=24:00:00
#SBATCH --partition=day-long
#SBATCH --nodes=1
#SBATCH --mem=5G
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --gres=gpu:1
echo $HOSTNAME

export LD_LIBRARY_PATH=/home/shared_write/gcc/installation/lib64:$LD_LIBRARY_PATH
export PATH=/home/shared_write/gcc/installation/bin:$PATH
bash /home/shared_write/gcc/amber_cuda/amber-interactive.sh

#--------------------------------------------------------------#

pmemd.cuda -O -i min.in -c system.rst -p system.parm -r min.rst -x min.nc -o min.out -inf min.info
pmemd.cuda -O -i heat1.in -o heat1.out -p system.parm -c min.rst -r heat1.rst -x heat1.nc -ref min.rst
pmemd.cuda -O -i heat2.in -o heat2.out -p system.parm -c heat1.rst -r heat2.rst -x heat2.nc -ref heat1.rst
pmemd.cuda -O -i equil.in -o equil.out -p system.parm -c heat2.rst -r equil.rst -x equil.nc -inf equil.info
pmemd.cuda -O -i prod.in -o prod.out -p system.parm -c equil.rst -r prod.rst -x prod.nc -inf prod.mdinfo
#pmemd.cuda -O -i pull.in -o pull.out -p system.parm -c equil.rst -r pull.rst -x pull.nc -inf pull.info
