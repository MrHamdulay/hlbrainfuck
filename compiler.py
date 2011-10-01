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

    def __init__(self):
        #yes, singletons are bad
        #XXX: get rid of this list and put it into thte compiler object
        if not hasattr(Register, 'registers'):
            Register.registers = []
        Register.registers.append(self)

    def _finalIndex(self):
        if index is None:
            raise 'Indexes have not been resolved'
        return index

#maps user defined registers to actual brainfuck registers
#user defined registers can have index [0...800ish]
class UserRegister(Register):
    pass

#temporary register used internally for calculations
class TempRegister(Register):
    pass

class Pointer:
    def __init__(self):
        self.pos = 0

    def move(self, index):
        self.pos += index

    def __int__(self):
        return self.pos

class Value:
    value = None
    register = None
    def __init__(self, register, value):
        assert isinstance(register, Register)
        self.register = register
        self.value = value

    #returns brainfuck string that creates this value
    def _fuckUp(self, curPointer):
        #return optimiseRepeat(self.value, '+')
        result = ''
        if self.register is not None:
            result += MovePointer(self.register._finalIndex())._fuckUp(curPointer)
        result += self.value * '+'
        return result


#move from index to another index
class MovePointer:
    offset = None
    def __init__(self, offset):
        self.offset = offset

    def _fuckUp(self, curPointer):
        delta = abs(int(curPointer) - self.offset)
        d = '<' if (int(curPointer) - self.offset) < 0 else '>'
        #return optimiseRepeat(delta)
        curPointer.move(self.offset)
        return d * delta

#[move to dest, increment, move back, decrement]
#from from one register to many registers
class Move:
    _command = 'move'
    _ars = 2
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
        result = '%s[' % MovePointer(last)._fuckUp(curPointer)
        for register in self.toRegisters:
            #move to dest, incremement
            result += '%s+' % MovePointer(register._finalIndex()).fuckUp(curPointer)

        #move from last to beginning
        result += '%s]' % MovePointer(self.fromRegister._finalIndex())._fuckUp(curPointer)
        return result

class Copy:
    _command = 'copy'
    _args = 2
    offset = None
    left = False

    def __init__(self, fromRegister, toRegister):
        assert isinstance(fromRegister, Register) and isinstance(toRegister, Register)
        self.fromRegister = fromRegister
        self.toRegister = toRegister

    def _fuckUp(self, curPointer):
        temp = TempRegister()
        return '%s%s' % (Move(self.fromRegister, [temp, self.toRegister])._fuckUp(curPointer),
                           Move(temp, [self.fromRegister])._fuckUp(curPointer))

class Add:
    def __init__(self, x, y):
        pass

class Compiler:
    proggy = None

    def __init__(self, proggy):
        self.proggy = proggy
        self.pointer = Pointer()

    def resolveRegisters(self):
        if not hasattr(Register, 'registers'):
            return
        #for some reason i thought this would be a lot more complicated
        for i, register in enumerate(Register.registers):
            register.index = i

    #commands are [command, args...]
    def compile(self, proggy):
        for line in proggy:
            l = line.split(' ')
        pass

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
