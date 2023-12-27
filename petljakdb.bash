#!/bin/bash
echo $HOSTNAME
singularity instance start --bind ${HOME}     --bind ${PWD}/mysql/var/lib/mysql/:/var/lib/mysql     --bind ${PWD}/mysql/run/mysqld:/run/mysqld     /gpfs/data/petljaklab/containers/isu_mysql/mysql.simg mysql
singularity run instance://mysql
tail -f /dev/null