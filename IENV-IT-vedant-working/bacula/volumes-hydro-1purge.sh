#!/bin/bash
bconsole -c /etc/bacula/bconsole.conf <<END_OF_DATA
purge yes volume=hydro-e-proj-1030
purge yes volume=hydro-e-proj-1031
purge yes volume=hydro-e-proj-1032
purge yes volume=hydro-e-proj-1033
purge yes volume=hydro-e-proj-1034
purge yes volume=hydro-e-proj-1035
purge yes volume=hydro-e-proj-1036
purge yes volume=hydro-e-proj-1037
purge yes volume=hydro-e-proj-1038
purge yes volume=hydro-e-proj-1039
purge yes volume=hydro-e-proj-1040
purge yes volume=hydro-e-proj-1041
purge yes volume=hydro-e-proj-1042
END_OF_DATA
