import argparse
from subprocess import call
from os import path, chdir, makedirs, listdir
from collections import defaultdict
import re
import datetime
from json import load

# ----------------------- Vars -----------------------

temp_file = "short.log.git"
shortlog_cmd = "git log --pretty=format:\"%an|%ai\" > " + temp_file
cleanup_cmd = "rm -f " + temp_file
map_ = defaultdict(list)
base_contributors = []
lookup = {}
template = 'Student: {}\nTotal commits: {}\nCloned on: {}\nFirst Commit Date: {}\nLast Commit Date: {}\n' + '-' * 50 + '\n'
template_clone_only = 'Student: {}\nTotal commits: 0\nCloned on:{}\n' + '-' * 50 + '\n'

# ----------------------- Parse -----------------------

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', dest='input_dir', help='Input directory of git repos')
parser.add_argument('-o', '--output', dest='out_dir', default='./out', help='Write back directory. Defaults to .out')
parser.add_argument('-g', '--grades', dest='grades_file', default=None, help='Path to grade file, formatted as '
                                                                             'name:grade. Optional, will produce less'
                                                                             'feedback if not given')
parser.add_argument('-b', '--base-contributor-files', dest='base_contributors', default='.contributorignore',
                    help='Path to file of people to be ignored. Defaults to .contributorignore')
parser.add_argument('-e', '--email', dest='email_file', default='.email', help='Text file of the email. '
                                                                               'Defaults to .email')
parser.add_argument('-l', '--lookup', dest='lookup_table', default='.translate',
                    help='Translation table for GitHub names to student names as a JSON file '
                         'formatted like {GH name: Real name,...}. Defaults to .translate')
parser.add_argument('assignment', help='One or more GitHub project names. Input folder names default to this')
# parser.add_argument('-f', '--figure', dest='figure_en', default=False, type=bool, help='Generate plot of commit '
#                                                                                        'frequency and start date vs '
#                                                                                        'grade')
args = parser.parse_args()

# ----------------------- Error Check -----------------------
input_dir = ''
if args.input_dir is None:
    input_dir = args.assignment
elif path.exists(args.input_dir) or path.isdir(args.input_dir):
    input_dir = args.input_dir
else:
    raise ValueError('Input must be a directory and exist')
out_dir = path.abspath(args.out_dir)
if not path.exists(path.dirname(out_dir)):
    makedirs(path.dirname(out_dir))
grade_file = path.abspath(args.grades_file) if (args.grades_file and path.exists(args.grades_file)) else None

# ----------------------- Load some files -----------------------

if path.exists(args.base_contributors) and path.isfile(args.base_contributors):
    with open(args.base_contributors, 'r') as contributors:
        base_contributors = [name[:-1] for name in contributors.readlines()]

if path.exists(args.lookup_table) and path.isfile(args.lookup_table):
    with open(args.lookup_table, 'r') as f:
        lookup = load(f)
else:
    raise ValueError('Lookup table does not exist')

# ----------------------- Email File -----------------------

assignment_re = re.compile(args.assignment)
if args.email_file:
    subject_line_re = re.compile('^Subject:.+')
    date_line_re = re.compile('^Date:.+')
    contributor = None
    with open(args.email_file, 'r') as emails:
        for line in emails.readlines():
            if re.match(subject_line_re, line):
                repo_name = line.split('/')[1].split(' ')[0]
                if repo_name.startswith(args.assignment):
                    GH_name = re.split(assignment_re, repo_name)[1][1:]
                    try:
                        contributor = lookup[GH_name]
                    except KeyError as e:
                        print('Cannot find user', GH_name, 'specified in email')
                        contributor = None
            elif contributor and re.match(date_line_re, line):
                date_str = ' '.join(line.split(' ')[1:4])
                map_[contributor].append(datetime.datetime.strptime(date_str, '%B %d, %Y').date())
                contributor = None

# ----------------------- Git Stuff -----------------------

chdir(input_dir)
for submission_dir in listdir('.'):
    if (not path.isdir(submission_dir)) or submission_dir.startswith('.'):
        continue
    chdir(submission_dir)
    try:
        name = lookup[re.split(assignment_re, submission_dir)[1][1:]]
    except KeyError as e:
        print('Cannot find user', re.split(assignment_re, submission_dir)[1][1:])
        name = re.split(assignment_re, submission_dir)[1]
    call(shortlog_cmd.split('\\s+'), shell=True)
    with open(temp_file, 'r') as shortlog:
        for line in shortlog:
            parts = line.split('|')
            contributor = parts[0]
            date_stamp = parts[1].split(' ')[0]
            if contributor in base_contributors:
                continue
            else:
                date = datetime.datetime.strptime(date_stamp, '%Y-%m-%d').date()
                map_[name].append(date)  # Will be sorted in reverse chron because of git log
    call(cleanup_cmd, shell=True)
    chdir('..')

# ----------------------- Build Output File -----------------------
sb = []
for contributor in map_.keys():
    commit_dates = map_[contributor]
    clone_date = commit_dates[0]
    commit_counts = len(commit_dates)
    if commit_counts > 1:
        first_commit = commit_dates[-1]
        last_commit = commit_dates[1]
        sb.append(template.format(contributor, commit_counts, clone_date, first_commit, last_commit))
    else:
        sb.append(template_clone_only.format(contributor, clone_date))

with open(out_dir, 'w+') as out:
    out.writelines(sb)
