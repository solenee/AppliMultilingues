#coding:utf-8

import sys
nb_lines = int(sys.argv[1])
lines = []
with open("Donnees/extracted/index.fr", "r") as f:
	for i in range(nb_lines):
		lines.append(f.readline())
		
with open("Donnees/extracted/index.subfr", "w") as f:
	for line in lines:
		f.write(line)

