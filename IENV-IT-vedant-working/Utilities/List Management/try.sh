#!/bin/bash

for i in `cat jmie-last-first-uniq`;do 
	first=$(echo ${i,,} |cut -f1 -d,)
	last=$(echo ${i,,} |cut -f2 -d,)
	firstcase=${first^}
	lastcase=${last^}
	echo $lastcase $firstcase ---------------------------
	grep $lastcase ucd.csv |grep $firstcase
	#grep $lastcase ucd-names.csv |grep $firstcase
done
