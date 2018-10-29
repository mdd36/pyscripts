import argparse
from matplotlib import pyplot
from sys import stderr
from subprocess import call
from os import path

shortlog_cmd = "git shortlog > {}.git.log"

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', dest='input_dir', default='.', help='Input directory of git repos')
parser.add_argument('-o', '--output', dest='out_dir', default='./out', help='Write back directory')
parser.add_argument('-f', '--figure', dest='figure_en', default=False, type=bool, help='Generate plots of commit'
                                                                                       ' frequency')

