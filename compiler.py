#!/usr/bin/env python2
import sys

#not always the best but good enough
def findBestBase(rep):
    bestBase = 1
    best = rep
    for i in range(2, 20):
        length = rep / i + rep % i
        if length < best:
            best = length
            bestBase = i
    return bestBase

def optimiseRepeat(rep, command):
    bestBase = findBestBase(rep)
    d = command
    if bestBase == 1:
        return d * rep
    return '%s[%s]%s' % (d * (rep/bestBase), d * bestBase, d*(rep%i))

class Register:
    pass

#maps user defined registers to actual brainfuck registers
#user defined registers can have index [0...800ish]
class UserRegister(Register):
    mappedOnto = None

    #set the index value of the internal register this register is mapped onto
    def _map(self, index):
        self.mappedOnto = index1000ish

#temporary register used internally for calculations
class TempRegister(Register):
    index = 0
    def __init__(self, index):
        self.index = index


class Value:
    value = None
    def __init__(self, value):
        self.value = value

    #returns brainfuck string that creates this value
    def _fuckUp(self):
        return optimiseRepeat(self.value, '+')


#move from index to another index
class Move:
    offset = None
    left = False
    def __init__(self, left, offset):
        self.offset = offset
        self.left = left

    def _fuckUp(self):
        d = '<' if self.left else '>'
        return optimiseRepeat(self.offset)



class Command:
    pass

class Add(Command):
    def __init__(self, x, y):
        pass

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
