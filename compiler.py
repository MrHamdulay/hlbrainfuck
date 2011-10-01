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

#bleh this doesn't work, need to use temporary registers and still need to figure that out
def optimiseRepeat(rep, command):
    bestBase = findBestBase(rep)
    d = command
    if bestBase == 1:
        return d * rep
    return '%s[%s]%s' % (d * (rep/bestBase), d * bestBase, d*(rep%i))

class Register:
    index = None
    def _finalIndex(self):
        return index

#maps user defined registers to actual brainfuck registers
#user defined registers can have index [0...800ish]
class UserRegister(Register):
    pass

#temporary register used internally for calculations
class TempRegister(Register):
    pass

class Value:
    value = None
    def __init__(self, value):
        self.value = value

    #returns brainfuck string that creates this value
    def _fuckUp(self, curPointer):
        #return optimiseRepeat(self.value, '+')
        return self.value * '+'


#move from index to another index
class MovePointer:
    pos = None
    def __init__(self, pos):
        self.offset = abs(pos)

    def _fuckUp(self, curPointer):
        delta = abs(curPointer - self.pos)
        d = '<' if (curPointer - self.pos) < 0 else '>'
        #return optimiseRepeat(delta)
        return d * delta

#[move to dest, increment, move back, decrement]
#from from one register to many registers
class Move:
    fromRegister = None
    toRegister = None

    def __init__(self, fromRegister, toRegisters):
        assert isinstance(fromRegister, Register)
        for register in toRegisters:
            assert isinstance(register, Register)

        self.fromRegister = fromRegister
        self.toRegisters = toRegisters

    def _fuckUp(self, curPointer):
        #move to from register position
        last = self.fromRegister._finalIndex()
        result = '%s[' % MovePointer(last)._fuckUp(curPointer)
        for register in self.toRegisters:
            #move to dest, incremement
            result += '%s+' % MovePointer(register._finalIndex()).fuckUp(last)
            last = register._finalIndex()

        #move from last to beginning
        result += '%s]' % MovePointer(self.fromRegister._finalIndex())._fuckUp(self.toRegisters[-1]._toFinalIndex())
        return result

class Copy:
    offset = None
    left = False

    def __init__(self, fromRegister, toRegister):
        assert isinstance(fromRegister, Register) and isinstance(toRegister, Register)
        self.fromRegister = fromRegister
        self.toRegister = toRegister

    def _fuckUp(self):
        temp = TempRegister()
        result = Move(
        pass

class Add:
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
