import argparse
from matplotlib import pyplot
from sys import stderr
from subprocess import call
from os import path, chdir, makedirs, listdir, getcwd
from collections import defaultdict
import datetime

# ----------------------- Vars -----------------------

temp_file = "short.log.git"
shortlog_cmd = "git log --pretty=format:\"%an|%ai\" > " + temp_file
cleanup_cmd = "rm -f " + temp_file
map_ = defaultdict(list)
base_contributors = []
template = 'Student: {}\nTotal commits: {}\nFirst Commit Date: {}\nLast Commit Date: {}\n' + '-'*50 + '\n'

# ----------------------- Parse -----------------------

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', dest='input_dir', default='.', help='Input directory of git repos')
parser.add_argument('-o', '--output', dest='out_dir', default='./out', help='Write back directory')
parser.add_argument('-g', '--grades', dest='grades_file', default=None, help='Path to grade file, formatted as '
                                                                             'name:grade')
parser.add_argument('-b', '--base-contributor-files', dest='base_contributors', default='.contributorignore',
                    help='Path to file of people to be ignored')
# parser.add_argument('-f', '--figure', dest='figure_en', default=False, type=bool, help='Generate plot of commit '
#                                                                                        'frequency and start date vs '
#                                                                                        'grade')
args = parser.parse_args()

# ----------------------- Error Check -----------------------

if not (path.exists(args.input_dir) or path.isdir(args.input_dir)):
    raise ValueError('Input must be a directory and exist')
out_dir = path.abspath(args.out_dir)
if not path.exists(path.dirname(out_dir)):
    makedirs(path.dirname(out_dir))
grade_file = path.abspath(args.grades_file) if (args.grades_file and path.exists(args.grades_file)) else None

# ----------------------- Load some files -----------------------

if path.exists(args.base_contributors) and path.isfile(args.base_contributors):
    with open(args.base_contributors, 'r') as contributors:
        base_contributors = [name[:-1] for name in contributors.readlines()]
        print(base_contributors)

# ----------------------- Git Stuff -----------------------

chdir(args.input_dir)
for submission_dir in listdir('.'):
    if (not path.isdir(submission_dir)) or submission_dir.startswith('.'):
        continue
    chdir(submission_dir)
    # print(getcwd())
    call(shortlog_cmd.split('\\s+'), shell=True)
    with open(temp_file, 'r') as shortlog:
        for line in shortlog:
            parts = line.split('|')
            name = parts[0]
            date_stamp = parts[1].split(' ')[0]
            if name in base_contributors:
                continue
            else:
                date = datetime.datetime.strptime(date_stamp, '%Y-%m-%d').date()
                map_[name].append(date) # Will be sorted in reverse chron because of git log
    call(cleanup_cmd, shell=True)
    chdir('..')

# ----------------------- Build Output File -----------------------
sb = []
for name in map_.keys():
    commit_dates = map_[name]
    first_commit = commit_dates[-1]
    last_commit = commit_dates[0]
    commit_counts = len(commit_dates)
    sb.append(template.format(name, commit_counts, first_commit, last_commit))

with open(out_dir, 'w+') as out:
    out.writelines(sb)
