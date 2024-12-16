#!/bin/bash
bconsole -c /etc/bacula/bconsole.conf <<END_OF_DATA
delete yes volume=hydro-e-proj-1030
delete yes volume=hydro-e-proj-1031
delete yes volume=hydro-e-proj-1032
delete yes volume=hydro-e-proj-1033
delete yes volume=hydro-e-proj-1034
delete yes volume=hydro-e-proj-1035
delete yes volume=hydro-e-proj-1036
delete yes volume=hydro-e-proj-1037
delete yes volume=hydro-e-proj-1038
delete yes volume=hydro-e-proj-1039
delete yes volume=hydro-e-proj-1040
delete yes volume=hydro-e-proj-1041
delete yes volume=hydro-e-proj-1042
END_OF_DATA
