"""
pull-all.py

Utility to pull all submissions for ECE 350.

Example usage to pull all pc1 submissions, if pc1 was due at 11:59:59 on September 11, 2018:

    python path/to/pull-all.py 1 18-09-11

The verbose flag (-v) will direct git command output to your terminal window, as well as give more detailed status
messages during the program

The new input flag (-i) should be followed by a path to a text file containing all github names for students in the
class, on per line. If no -i flag is given, then the last set of github usernames is used, stored in it's own file away
from the caller. An example flag and path is shown below:

    -i ~/TA/350/github_name.txt

The output flag (-o) will redirect output from the current director to the one specifed after the flag. By default, all
projects are cloned into the cwd, so -o is normally desired. The directories will be made if they don't already exist.
For example,

    -o ~/TA/350/pc1

will clone all projects into the folder ~/TA/350/pc1
"""

from subprocess import call, DEVNULL
from sys import argv, stderr, stdout
from os import path, getcwd, chdir, makedirs

# ----------------------- Globals -----------------------

usage = """Usage error, should be
    python pull-all <pc-number> <due-date like YY-MM-DD> [<-v> <-i /list/of/netids> <-o /export/path>]"""

last_netid_set_path = path.expanduser('~') + '/pyscripts/.dat/netids/last'
pull_cmd = 'git clone git@github.com:DukeECE350/{}-{}.git'  # pc number, github name
branch_clean = 'git branch -d grading'
rollback_cmd = """git checkout `git rev-list -n 1 --before="{} 11:59" master`"""
branch_cmd = 'git branch grading'
checkout_cmd = 'git checkout grading'

if not path.exists(path.expanduser('~') + '/pyscripts/.dat/netids'):
    makedirs(path.expanduser('~') + '/pyscripts/.dat/netids')


# ----------------------- Parse -----------------------

verbose = False
input_dir = last_netid_set_path
output_dir = './pulled/{}'

if len(argv) < 3 or not 0 <= int(argv[1]) <= 4:
    print(usage, file=stderr)
    exit(1)

pc_number = 'pc'+argv[1]
rollback_cmd = rollback_cmd.format('20' + argv[2])

verbose = '-v' in argv

out = DEVNULL

if verbose:
    out = open(stdout, 'w')

try:
    in_dex = argv.index('-i')
except ValueError as e:
    in_dex = -1

try:
    out_dex = argv.index('-o')
except ValueError as e:
    out_dex = -1

if in_dex > -1:
    input_dir = argv[in_dex+1]

if out_dex > -1:
    output_dir = argv[out_dex+1]

# ----------------------- Load GH Names -----------------------
print('Loading names from file {}...'.format(input_dir))
file = open(input_dir, 'r')
names = [name[:-1] for name in file.readlines()]
file.close()

# ----------------------- Pull -----------------------

print('Pulling and rolling back...')
no_sub = []
if not path.exists(output_dir):
    makedirs(output_dir)

chdir(output_dir)

for github_name in names:
    if verbose:
        print('Pulling {} into {}/{}-{}...'.format(github_name, getcwd(), pc_number, github_name))
    cmd = pull_cmd.format(pc_number, github_name)
    call(cmd.split('\\s+'), shell=True, stdout=out)
    if not path.exists('{}-{}'.format(pc_number, github_name)):
        no_sub.append(github_name)
        continue
    chdir('{}-{}'.format(pc_number, github_name))
    call(branch_clean, shell=True, stdout=out)
    call(rollback_cmd, shell=True, stdout=out)
    call(branch_cmd, shell=True, stdout=out)
    call(checkout_cmd, shell=True, stdout=out)
    chdir('..')

# ----------------------- Save Dir for next time -----------------------

if verbose:
    print('Saving netid for next time...')
with open(last_netid_set_path, 'w+') as file:
    file.writelines('\n'.join(names))


print('Done, following students made no submission: {}'.format(', '.join(no_sub)))
