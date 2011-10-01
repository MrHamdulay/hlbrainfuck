#!/usr/bin/env python2
import sys

class Register:
    index = 0
    def __init__(self, index):
        self.index = index

#maps user defined registers to actual brainfuck registers
#user defined registers can have index [0...800ish]
class UserRegister(Register):
    mappedOnto = None

    #set the index value of the internal register this register is mapped onto
    def _map(self, index):
        self.mappedOnto = index1000ish

#temporary register used internally for calculations
class TempRegister(Register):
    pass

class Value:
    value = None
    def __init__(self, value):
        self.value = value

    #returns brainfuck string that creates this value
    def _fuckUp(self):
        pass

class Command:
    pass

#move from index to another index
class Move:
    offset = None
    left = False
    def __init__(self, left, offset):
        self.offset = offset
        self.left = left

    def _fuckUp(self):
        bestBase = 1
        best = self.offset
        for i in range(2, 20):
            length = self.offset / i + 2 + i + self.offset % i
            if length < best:
                best = length
                bestBase = i
        d = '<' if self.left else '>'
        return '%s[%s]%s' % (d * (self.offset/bestBase), d * bestBase, d*(self.offset%i))

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
