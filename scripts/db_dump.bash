#!/bin/bash
file=$1
. /etc/bashrc &> /dev/null
. ~/.bash_profile &> /dev/null
. ~/.bashrc &> /dev/null
module load mariadb
cd /gpfs/data/petljaklab/petljakdb/
echo $file
mysqldump petljakdb > /gpfs/data/petljaklab/petljakdb/dumps/$file
