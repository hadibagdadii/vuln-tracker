#!/bin/bash
bconsole -c /etc/bacula/bconsole.conf <<END_OF_DATA
prune yes volume=hydro-e-proj-1030
prune yes volume=hydro-e-proj-1031
prune yes volume=hydro-e-proj-1032
prune yes volume=hydro-e-proj-1033
prune yes volume=hydro-e-proj-1034
prune yes volume=hydro-e-proj-1035
prune yes volume=hydro-e-proj-1036
prune yes volume=hydro-e-proj-1037
prune yes volume=hydro-e-proj-1038
prune yes volume=hydro-e-proj-1039
prune yes volume=hydro-e-proj-1040
prune yes volume=hydro-e-proj-1041
prune yes volume=hydro-e-proj-1042
END_OF_DATA
