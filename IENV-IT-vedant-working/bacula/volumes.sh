#!/bin/bash

voldel=volumes-hydro-delete.list
voldir=/z0/proj/bacula/vols/hydro-e-proj

###################

function prune {
bconsole -c /etc/bacula/bconsole.conf <<END_OF_DATA
prune yes volume=$i
END_OF_DATA
}
function purge {
bconsole -c /etc/bacula/bconsole.conf <<END_OF_DATA
purge yes volume=$i
END_OF_DATA
}
function delete {
bconsole -c /etc/bacula/bconsole.conf <<END_OF_DATA
delete yes volume=$i
END_OF_DATA
}

for i in $(cat $voldel);do echo $i;
#	prune
#	purge
#	delete
	rm $voldir/$i
done
