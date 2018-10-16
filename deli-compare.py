from sys import argv, exit
from os import path

if len(argv) < 3:
    print("Error: Usage us python3 deli-compare.py file1 file2")
    exit(1)

file1 = argv[1]
file2 = argv[2]

if not path.exists(file1) or not path.exists(files):
    print("Error: One file does not exist")
    exit(1)

flist1 = []
flist2 = []

with open(file1, 'r'), open(file2, 'r') as f1, f2:
    pass