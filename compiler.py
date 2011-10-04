#!/usr/bin/env python2
import sys
from collections import defaultdict

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
        if hasattr(Register, 'disabled'):
            raise RuntimeException('Cannot create registers in fuck up phase')
        if not hasattr(Register, 'registers'):
            Register.registers = []
        Register.registers.append(self)

    def _finalIndex(self):
        if self.index is None:
            raise RuntimeException('Indexes have not been resolved')
        return self.index

#maps user defined registers to actual brainfuck registers
#user defined registers can have index [0...800ish]
class UserRegister(Register):
    pass

#temporary register used internally for calculations
#TODO: reassign tempregisters to other commands when they're no longer used
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
    dest = None
    def __init__(self, dest):
        self.dest = dest

    def _fuckUp(self, curPointer):
        delta = abs(int(curPointer) - self.dest)
        d = '<' if (int(curPointer) - self.dest) < 0 else '>'
        #return optimiseRepeat(delta)
        curPointer.move(self.dest)
        return d * delta

#[move to dest, increment, move back, decrement]
#from from one register to many registers
class Move:
    _command = 'move'
    _ars = 2
    fromRegister = None
    fromVal = None
    toRegister = None

    def __init__(self, fromRegister, toRegisters):
        if not isinstance(toRegisters, (tuple, list)):
            toRegisters = (toRegisters,)
        for register in toRegisters:
            assert isinstance(register, Register)

        self.fromRegister = fromRegister
        self.toRegisters = toRegisters

        if isinstance(self.fromRegister, int):
            self.fromVal = self.fromRegister
            self.fromRegister = TempRegister()

    def _fuckUp(self, curPointer):
        #move to from register position
        result = ''

        if self.fromVal is not None:
            result += Value(self.fromRegister, self.fromVal)._fuckUp(curPointer)

        print self.fromRegister
        result += '%s[' % MovePointer(self.fromRegister._finalIndex())._fuckUp(curPointer)
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
        self.temp = TempRegister()

    def _fuckUp(self, curPointer):
        return '%s%s' % (Move(self.fromRegister, [self.temp, self.toRegister])._fuckUp(curPointer),
                           Move(self.temp, [self.fromRegister])._fuckUp(curPointer))

class Add:
    def __init__(self, x, y):
        pass

class Compiler:
    proggy = None
    pointer = None

    def __init__(self, proggy):
        self.proggy = proggy
        self.pointer = Pointer()

    def resolveRegisters(self):
        if not hasattr(Register, 'registers'):
            return
        #for some reason i thought this would be a lot more complicated
        for i, register in enumerate(Register.registers):
            register.index = i

    commands = {'copy': Copy,
                'move': Move,
                'add': Add,}

    #commands are [command, args...]
    def compile(self):
        result = ''
        commands = []
        registers = defaultdict(Register)

        for line in self.proggy.split('\n'):
            l = line.split(' ')
            command, args = l[0], l[1:]
            for i in xrange(len(args)):
                try:
                    number = int(args[i])
                    args[i] = TempRegister()
                    commands.append(Value(args[i], number))
                except ValueError:
                    try:
                        if args[i][0] == 'r':
                            args[i] = registers[int(args[i][1:])]
                    except ValueError:
                        pass

            print 'Args', (command, args)

            if command not in self.commands:
                print 'Unsupported command: \'%s\'' % l[0]
            else:
                commands.append(self.commands[command](*args))

        Register.disabled = True
        result = ''.join([x._fuckUp(self.pointer) for x in commands])

        return result


if __name__ == '__main__':
    outputfile = sys.stdout
    proggy = ''

    if len(sys.argv) > 1:
        inputfilename = sys.argv[1]
        with open(inputfilename, 'r') as f:
            for line in f:
                proggy += line
        if len(sys.argv) > 2:
            outputfile = open(sys.argv[2], 'w')
    else:
        print 'python ./compiler.py [filename]'
        sys.exit(1)

    compiler = Compiler(proggy)
    compiler.compile()
    outputfile.write(compiler.brainfuck())
    outputfile.close()
