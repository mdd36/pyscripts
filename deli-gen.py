#!/usr/bin/env python

from sys import argv
from os import mkdir, path
from random import randint
from shutil import rmtree

num_cashiers = 10
num_orders = 20

if len(argv) > 1:
    num_cashiers = int(argv[1])

if len(argv) > 2:
    num_orders = int(argv[2])

if path.exists("./cashiers"):
    rmtree("./cashiers")

mkdir("./cashiers")

total_orders = 0

for i in range(num_cashiers):
    orders = []
    orders_in_file = num_orders if num_orders > 0 else randint(1, 500)
    total_orders += orders_in_file
    for j in range(orders_in_file):
        orders.append(str(randint(0, 999)))

    with open("./cashiers/sw.in{}".format(i), 'w+') as file:
        file.write('\n'.join(orders))

with open('./cashiers/.meta-inf', 'w+') as file:
    file.write(str(total_orders) + "\n")
