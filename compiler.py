#!/usr/bin/env python2
import sys

class Register:
    index = 0
    mappedOnto = None
    def __init__(self, index):
        self.index = index

    #set the index value of the internal register this register is mapped onto
    def _map(self, index):
        self.mappedOnto = index

class Compiler:
    proggy = None

    def __init__(self, proggy):
        self.proggy = proggy

    def add(self, x, y):
        pass

    #commands are [command, args...]
    def compileCommand(self, command):
        if isinstance(command, str):
            command = command.split(' ')

if __name__ == '__main__':
    outputfile = sys.stdout
    proggy = None

    if len(sys.argv) > 1:
        inputfilename = sys.argv[1]
        with open(inputfilename, 'r') as f:
            proggy = f.read()
        if len(sys.argv) > 2:
            outputfile = open(sys.argv[2], 'w')
    else:
        print 'python ./compiler.py [filename]'
        sys.exit(1)

    compiler = Compiler(proggy)
    compiler.compile()
    outputfile.write(compiler.brainfuck())
    outputfile.close()
