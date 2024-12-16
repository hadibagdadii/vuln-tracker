#!/bin/bash

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

for i in $(cat volumes-s1-g-delete.lis);do echo $i;
#	prune
#	purge
#	delete
#	rm /z0/proj/bacula/vols/s1-g-projects/$i
done
