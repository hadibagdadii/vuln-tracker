#!/bin/bash

# delete and purge all volumes in a pool
# delete volume file from filesystem
#
# pool name
pool=hydro-e-proj

# pool path
ppath=/z0/proj/bacula/vols/$pool

for i in `echo "list volumes" |bconsole |grep $pool |awk {'print $4'}`;do
        echo "purge volume=$i yes" |bconsole
        echo "delete volume=$i yes" |bconsole
        echo =============================
        rm $ppath/$i
        df -h .
done
