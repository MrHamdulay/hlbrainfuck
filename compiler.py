#!/usr/bin/env python2
import sys
from collections import defaultdict

class Register:
    index = None
    modified = False

    def __init__(self):
        #yes, singletons are bad
        #XXX: get rid of this list and put it into thte compiler object
        if hasattr(Register, 'disabled'):
            raise Exception('Cannot create registers in fuck up phase')
        if not hasattr(Register, 'registers'):
            Register.registers = []
        Register.registers.append(self)
        self.modified = False

    def _finalIndex(self):
        if self.index is None:
            raise Exception('Indexes have not been resolved')
        return self.index

    def __repr__(self):
        return '<Register index: %s >' % (self.index if self.index is not None else 'unresolved')

#maps user defined registers to actual brainfuck registers
#user defined registers can have index [0...800ish]
class UserRegister(Register):
    pass

#temporary register used internally for calculations
#TODO: reassign tempregisters to other commands when they're no longer used
class TempRegister(Register):
    def __repr__(self):
        return '<TempRegister index: %s>' % (str(self.index) if self.index is not None else 'unresolved')
    pass

class Pointer:
    def __init__(self):
        self.pos = 0

    def move(self, index):
        self.pos = index

    def __int__(self):
        return self.pos

    def __repr__(self):
        return '<Pointer pos: %d>' % self.pos

#gives registers a value
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
            self.register.modified = True
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
        d = '<' if (int(curPointer) - self.dest) > 0 else '>'
        #return optimiseRepeat(delta)
        curPointer.move(self.dest)
        return d * delta

class Add:
    _command = 'add'
    destRegister = None
    fromRegister = None
    temp = None
    copy = None

    def __init__(self, destRegister, fromRegister):
        assert isinstance(destRegister, Register) and isinstance(fromRegister, Register)
        self.destRegister = destRegister
        self.fromRegister = TempRegister()
        self.copy = Copy(fromRegister, self.fromRegister)

    def _fuckUp(self, curPointer):
        result = self.copy._fuckUp(curPointer)
        result += MovePointer(self.fromRegister._finalIndex())._fuckUp(curPointer)
        result += '[%s+%s-]' % (MovePointer(self.destRegister._finalIndex())._fuckUp(curPointer),
                                MovePointer(self.fromRegister._finalIndex())._fuckUp(curPointer))
        return result

class Multiply:
    _command = 'multiply'

    destRegister = None
    fromRegister = None
    temp = None
    move = None
    add = None

    def __init__(self, destRegister, fromRegister):
        assert isinstance(destRegister, Register) and isinstance(fromRegister, Register)
        self.destRegister = destRegister
        self.fromRegister = fromRegister
        self.temp = TempRegister()
        self.move = Move(destRegister, self.temp)
        self.add = Add(self.destRegister, self.fromRegister)

    def _fuckUp(self, curPointer):
        result = self.move._fuckUp(curPointer)
        result += MovePointer(self.temp._finalIndex())._fuckUp(curPointer)
        result += '[%s%s%s-]' % (MovePointer(self.destRegister._finalIndex())._fuckUp(curPointer),
                                 self.add._fuckUp(curPointer),
                                 MovePointer(self.temp._finalIndex())._fuckUp(curPointer))
        return result


class Subtract:
    _command = 'subtract'

    def __init__(self, destRegister, fromRegister):
        assert isinstance(destRegister, Register) and isinstance(fromRegister, Register)
        self.destRegister = destRegister
        self.fromRegister = TempRegister()
        self.copy = Copy(fromRegister, self.fromRegister)

    def _fuckUp(self, curPointer):
        result = self.copy._fuckUp(curPointer)
        result += MovePointer(self.fromRegister._finalIndex())._fuckUp(curPointer)
        result += '[%s-%s-]' % (MovePointer(self.destRegister._finalIndex())._fuckUp(curPointer),
                                MovePointer(self.fromRegister._finalIndex())._fuckUp(curPointer))
        return result

#[move to dest, increment, move back, decrement]
#from from one register to many registers
class Move:
    _command = 'move'
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
        result = ''

        #clear all destination registers
        for register in self.toRegisters:
            result += MovePointer(register._finalIndex())._fuckUp(curPointer)
            if register.modified:
                result += '[-]'
            register.modified = True

        if self.fromVal is not None:
            result += Value(self.fromRegister, self.fromVal)._fuckUp(curPointer)

        result += '%s[' % MovePointer(self.fromRegister._finalIndex())._fuckUp(curPointer)
        for register in self.toRegisters:
            #move to dest, incremement
            result += '%s+' % MovePointer(register._finalIndex())._fuckUp(curPointer)

        #move from last to beginning
        result += '%s-]' % MovePointer(self.fromRegister._finalIndex())._fuckUp(curPointer)
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
        self.toRegister.modified = True
        self.temp.modified = True

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
                'add': Add,
                'subtract': Subtract,
                'multiply': Multiply}

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

            if command not in self.commands:
                print 'Unsupported command: \'%s\'' % l[0]
            else:
                commands.append(self.commands[command](*args))

        self.resolveRegisters()

        Register.disabled = True
        for command in commands:
            print 'Command %s, pointer pos: %d' % (command, self.pointer.pos)
            result += command._fuckUp(self.pointer)

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
        print 'python ./compiler.py [filename] [output file name]'
        sys.exit(1)

    compiler = Compiler(proggy)
    brainfuck = compiler.compile()
    outputfile.write(brainfuck)
    outputfile.write('?\n')
    outputfile.close()
