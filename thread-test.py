from sys import argv, stderr
from os import path, listdir, mkdir
from random import randint

if len(argv) < 2:
    print('Error, usage is:\n\tpython3 ~/pyscripts/thread-test.py num_threads', file=stderr)
    exit(1)

out_dir = './test'
data_dir = '/home/matthew/pyscripts/.dat/thread-test/'
create_template = "thread_create((thread_startfunc_t) {}, (void *) {});"

if not path.exists(out_dir):
    mkdir(out_dir)

num_threads = int(argv[1])
existing_files = len([name for name in listdir(out_dir) if name.startswith('test') and name.endswith('.cc')])
methods_used = []
seen = set()
header = """
#include "../thread.h"
#include <fstream>
#include <cstdlib>
#include <iostream>
#include <cassert>

using namespace std;

int x = 0;
string* filename;

/**
 * TEST WITH {} THREADS
 */

void str_append(char s){{
    ofstream str;
    str.open(*filename, fstream::out | fstream::app);
    str << s;
    str.close();
}}

"""

main = """
int main(int argc, char** argv){
    string f = string(argv[1]);
    filename = &f;
    thread_libinit((thread_startfunc_t) spawn, NULL);
}
"""

with open('{}/test{}.cc'.format(out_dir, existing_files), 'w+') as file:
    file.write(header.format(num_threads))
    for i in range(num_threads):
        method_to_write = randint(1, 7)
        methods_used.append(create_template.format("method{}".format(method_to_write), "NULL"))
        if method_to_write in seen:
            continue
        seen.add(method_to_write)
        with open('{}method{}.cc'.format(data_dir, method_to_write), 'r') as method:
            file.write(''.join(method.readlines()))
            file.write("\n\n")
    file.write("void spawn(){")
    file.write("\n\t")
    file.write('\n\t'.join(methods_used))
    file.write('\n\tthread_yield();\n}')
    file.write(main)
