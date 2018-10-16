from os import listdir
from sys import argv, stderr
from subprocess import call

files = [name[:-3] for name in listdir('.') if name.endswith(".cc")]
compilers = ["g++", "gcc"]
build_command = "sudo {} -o  {}.o {}.cc {} ../libinterrupt.a -I. -Wall -lm -ldl -no-pie " \
                "-std=c++11 -g"
error_msg = "Error: correct usage is\n\tbuild-all /thread/lib/path <g++/gcc>"

compiler = "g++"
thread_build_resource = 'thread.o'

if len(argv) > 1:
    thread_build_resource = argv[1]
else:
    print(error_msg, file=stderr)
    exit(1)


if len(argv) > 2:
    if argv in compilers:
        compiler = argv[2]
    else:
        print(error_msg, file=stderr)
        exit(1)

for file in files:
    call(build_command.format(compiler, file, file, thread_build_resource).split("\\s+"), shell=True)
