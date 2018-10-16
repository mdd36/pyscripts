# 1. Generate a test suite
# 2. Build them all with correct threadlib
# 3. Run them
# 4. Remove all .o files
# 5. Build them again with our thread lib
# 6. Run them again
# 7. Compare corresponding files
# 8. Delete all files that passed

from sys import argv, stderr
from os import chdir
from subprocess import call

generate_call = "sudo python3 /home/matthew/pyscripts/thread-test.py {}"
build_call = "sudo python3 /home/matthew/pyscripts/build-all.py {}"
run_call = "sudo ./test{}.o {}"


correct_threadlib = 'thread.o'
user_threadlib = '../thread.cc'

test_count = 20
threads_per_test = 20

failures = 0

if len(argv) > 2:
    test_count = int(argv[1])

if len(argv) > 3:
    threads_per_test = int(argv[2])

# 1
print("Generating...")
for i in range(test_count):
    try:
        call(generate_call.format(threads_per_test).split("\\s+"), shell=True)
    except:
        print("Error in file generation", file=stderr)
        exit(1)

chdir("test")

# 2
try:
    print("Building with correct library...")
    call(build_call.format(correct_threadlib).split("\\s+"), shell=True)
except:
    print("Error in building correct .o files", file=stderr)
    exit(1)

# 3
print("Generating expected values...")
for i in range(test_count):
    outname = 'correct{}'.format(i)
    try:
        call(run_call.format(i, outname), shell=True)
    except:
        print("Error in running correct .o files", file=stderr)
        exit(1)

# 4
print("Removing .o files...")
try:
    call("sudo rm test*.o".split("\\s+"), shell=True)
except:
    print("Error in removing correct .o files", file=stderr)
    exit(1)

# 5
print("Building with user library...")
try:
    call(build_call.format(user_threadlib).split("\\s+"), shell=True)
except:
    print("Error in building with user lib", file=stderr)
    exit(1)

# 6
print("Generating actual values...")
for i in range(test_count):
    outname = 'user{}'.format(i)
    try:
        call(run_call.format(i, outname), shell=True)
    except:
        print("Error in running user .o files", file=stderr)
        exit(1)

# 7, 8
print("Comparing files and cleaning up...")
for i in range(test_count):
    last_failed = False
    with open('correct{}'.format(i), 'r') as expected, open('user{}'.format(i), 'r') as actual:
        if expected.readlines() != actual.readlines():
            print("Failure in test {}, preserving files on quit...".format(i))
            failures += 1
            last_failed = True

    if not last_failed:
        correct_rm = 'sudo rm correct{}'.format(i)
        user_rm = 'sudo rm  user{}'.format(i)
        test_rm = 'sudo rm test{}.cc'.format(i)
        exec_rm = 'sudo rm test{}.o'.format(i)
        try:
            call(correct_rm.split("\\s+"), shell=True)
            call(user_rm.split("\\s+"), shell=True)
            call(test_rm.split("\\s+"), shell=True)
            call(exec_rm.split("\\s+"), shell=True)
        except:
            print("Error in file cleanup", file=stderr)
            exit(1)

if failures == 0:
    print("Test passed without failures")
else:
    print("Test failed with {} failures".format(failures))
