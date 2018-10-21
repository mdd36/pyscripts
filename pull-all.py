from subprocess import call, DEVNULL
from sys import argv, stderr, stdout
from os import path, getcwd, chdir, makedirs

# ----------------------- Globals -----------------------

usage = """Usage error, should be
    python pull-all <pc-number> <due-date like YY-MM-DD> [<-v> <-i /list/of/netids> <-o /export/path>]
"""
last_netid_set_path = path.expanduser('~') + '/pyscripts/.dat/netids/last'
pull_cmd = "git clone git@github.com:DukeECE350/{}-{}.git"  # pc number, github name
rollback_cmd = "git checkout \'master@{{ {} 23:59:59 }}\'"

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
rollback_cmd.format('20' + argv[2])

verbose = '-v' in argv

if verbose:
    out = open(stdout, 'w')
else:
    out = DEVNULL

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

if not path.exists(output_dir):
    makedirs(output_dir)

chdir(output_dir)

for github_name in names:
    if verbose:
        print('Pulling {} into {}/{}-{}...'.format(github_name, getcwd(), pc_number, github_name))
    cmd = pull_cmd.format(pc_number, github_name)
    call(cmd.split('\\s+'), shell=True, stdout=out)
    if not path.exists('{}-{}'.format(pc_number, github_name)):
        continue
    chdir('{}-{}'.format(pc_number, github_name))
    call(rollback_cmd, shell=True, stdout=out)
    chdir('..')

# ----------------------- Save Dir for next time -----------------------

if verbose:
    print('Saving netid for next time...')
with open(last_netid_set_path, 'w+') as file:
    file.writelines('\n'.join(names))


print('Done')
