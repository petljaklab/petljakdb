#!/bin/bash
#SBATCH -t 01:00:00
#SBATCH -p cpu_dev
#SBATCH -e /gpfs/data/petljaklab/petljakdb/petljakdb.log
#SBATCH -o /gpfs/data/petljaklab/petljakdb/petljakdb.log
#SBATCH -J petljakdb.bash
echo $HOSTNAME
singularity instance start --bind ${HOME}     --bind ${PWD}/mysql/var/lib/mysql/:/var/lib/mysql     --bind ${PWD}/mysql/run/mysqld:/run/mysqld     /gpfs/data/petljaklab/containers/isu_mysql/mysql.simg mysql
singularity run instance://mysql
tail -f /dev/null
