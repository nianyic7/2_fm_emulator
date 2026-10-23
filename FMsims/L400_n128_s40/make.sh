#!/bin/bash
codedir="/home/nianyic/gadget4_development"
cwd=$(pwd)

source "/home/nianyic/arepo_my/module_ias.sh"
cd $codedir
make clean DIR=$cwd
make -j 8 DIR=$cwd
