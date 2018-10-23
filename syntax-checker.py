from sys import stderr
from os import path, makedirs, listdir
import argparse
from collections import defaultdict
import re


# ------------------- Parse -------------------
parser = argparse.ArgumentParser()
parser.add_argument('-s', dest='syntax_location', default='', help='Syntax document, regex supported')
parser.add_argument('-i', dest='input_dir', default='.', help='Directory of submissions')
parser.add_argument('-o', dest='out_file', default='./results', help='Result file location')
parser.add_argument('-c', dest='example_count', type=int, default=100, help='Number of violations saved to output')
parser.add_argument('-b', dest='base_files', nargs='*', default=[], help='Base file given to students')
args = parser.parse_args()

if not path.exists(args.input_dir):
    print('Specified input directory does not exist: {}'.format(args.input_dir), file=stderr)
    exit(1)

syntax_file = path.abspath(args.syntax_location)  # Will change to in dir, so need abs path for later
if not path.exists(syntax_file):
    print('Specified input syntax file does not exist: {}'.format(syntax_file), file=stderr)
    exit(1)


out_file = path.abspath(args.out_file)
if not path.exists(path.dirname(out_file)):
    makedirs(path.dirname(out_file))

# ------------------- Load files -------------------

print('Loading syntax reference...')

illegal_syntax = set()
whitespace = re.compile('^\s*$')

with open(syntax_file, 'r') as syntax_ref:
    for line in syntax_ref:
        if not whitespace.match(line):
            illegal_syntax.add(re.compile('(:?!//)\s*'+line[:-1]))

for_loop = re.compile('\s*(for)\s*(\([\w\W]*\))\s*(begin\s*:\s*[\w*]?)?\s*(/)*\s*[\S\s]*')
# ------------------- Search for illegal syntax -------------------

print('Starting search for illegal syntax...')

violations = defaultdict(list)
violation_count = defaultdict(int)
violation_condition = defaultdict(list)

submissions = listdir(args.input_dir)
for student in submissions:
    if not path.isdir(path.join(args.input_dir, student)):
        continue
    print('Checking student {}...'.format(student))
    files = [path.join(args.input_dir, student, file) for file in listdir(path.join(args.input_dir, student))
             if file.endswith('.v') and not (file.endswith('_tb.v') or file.endswith(r'testbench.v'))]
    for submitted_file in files:
        if path.basename(submitted_file) in args.base_files:
            continue
        with open(submitted_file, 'r') as file:
            for line_num, line in enumerate(file):
                for pattern in illegal_syntax:
                    if pattern.search(line) and not for_loop.match(line):
                        if violation_count[student] < args.example_count:
                            violations[student].append(path.basename(submitted_file) + " " + str(line_num+1) + ":\t"
                                                       + line.strip() + '\n')
                            violation_condition[student].append(pattern)
                        violation_count[student] += 1

# ------------------- Write back results -------------------
string_builder = []
for cheater in violations.keys():
    string_builder.append("Student {} has {}  matches, first {} shown below:\n".format(cheater[4:],
                          violation_count[cheater], min(args.example_count, violation_count[cheater])))
    for i in range(min(args.example_count, violation_count[cheater])):
        string_builder.append(violations[cheater][i])
    string_builder.append(('-' * 50) + '\n')

with open(out_file, 'w+') as out:
    out.write(''.join(string_builder))

print('Done')
