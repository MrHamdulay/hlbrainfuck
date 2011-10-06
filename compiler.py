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
#TODO: optimise this to make it use less + operators
class Value:
    value = None
    register = None
    tempRegister = None

    def __init__(self, register, value):
        assert isinstance(register, Register)
        self.register = register
        self.value = value
        self.tempRegister = TempRegister()

    #returns brainfuck string that creates this value
    def _fuckUp(self, compiler):
        curPointer = compiler.pointer
        result = ''
        if self.register is not None:
            self.register.modified = True
            result += MovePointer(self.register._finalIndex())._fuckUp(compiler)
        result += self.value * '+'


        result2 = ''
        result2 += MovePointer(self.tempRegister._finalIndex())._fuckUp(compiler)
        result2 += '+' * (self.value / 6)
        result2 += '['+MovePointer(self.register._finalIndex())._fuckUp(compiler)
        result2 += '+'*6 + MovePointer(self.tempRegister._finalIndex())._fuckUp(compiler) + '-]'
        result2 += MovePointer(self.register._finalIndex())._fuckUp(compiler)
        result2 += '+' * (self.value % 6)
        return result if len(result) < len(result2) else result2


#move from index to another index
class MovePointer:
    dest = None
    def __init__(self, dest):
        self.dest = dest

    def _fuckUp(self, compiler):
        curPointer = compiler.pointer
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

    def _fuckUp(self, compiler):
        curPointer = compiler.pointer
        result = self.copy._fuckUp(compiler)
        result += MovePointer(self.fromRegister._finalIndex())._fuckUp(compiler)
        result += '[%s+%s-]' % (MovePointer(self.destRegister._finalIndex())._fuckUp(compiler),
                                MovePointer(self.fromRegister._finalIndex())._fuckUp(compiler))
        return result

class Multiply:
    _command = 'multiply'

    destRegister = None
    arg1 = None
    arg2 = None
    temp = None
    copy = None
    add = None

    def __init__(self, arg1, arg2, destRegister):
        self.arg1 = arg1
        self.arg2 = arg2

        self.destRegister = destRegister
        self.temp = TempRegister()
        self.copy = Copy(arg1, self.temp)
        self.add = Add(self.destRegister, arg2)

    def _fuckUp(self, compiler):
        curPointer = compiler.pointer
        result = self.copy._fuckUp(compiler)
        result += MovePointer(self.temp._finalIndex())._fuckUp(compiler)
        result += '[%s%s%s-]' % (MovePointer(self.arg2._finalIndex())._fuckUp(compiler),
                                 self.add._fuckUp(compiler),
                                 MovePointer(self.temp._finalIndex())._fuckUp(compiler))
        return result

class Subtract:
    _command = 'subtract'

    def __init__(self, destRegister, fromRegister):
        assert isinstance(destRegister, Register) and isinstance(fromRegister, Register)
        self.destRegister = destRegister
        self.fromRegister = TempRegister()
        self.copy = Copy(fromRegister, self.fromRegister)

    def _fuckUp(self, compiler):
        curPointer = compiler.pointer
        result = self.copy._fuckUp(compiler)
        result += MovePointer(self.fromRegister._finalIndex())._fuckUp(compiler)
        result += '[%s-%s-]' % (MovePointer(self.destRegister._finalIndex())._fuckUp(compiler),
                                MovePointer(self.fromRegister._finalIndex())._fuckUp(compiler))
        return result

#[move to dest, increment, move back, decrement]
#from from one register to many registers
class Move:
    _command = 'move'
    fromRegister = None
    toRegister = None

    value = None

    def __init__(self, fromRegister, toRegisters):
        if not isinstance(toRegisters, (tuple, list)):
            toRegisters = (toRegisters,)
        for register in toRegisters:
            assert isinstance(register, Register)

        self.fromRegister = fromRegister
        self.toRegisters = toRegisters

        if isinstance(self.fromRegister, int):
            fromVal = self.fromRegister
            self.fromRegister = TempRegister()
            self.value = Value(self.fromRegister, self.fromVal)

    def _fuckUp(self, compiler):
        curPointer = compiler.pointer
        result = ''

        #clear all destination registers
        for register in self.toRegisters:
            result += MovePointer(register._finalIndex())._fuckUp(compiler)
            if register.modified:
                result += '[-]'
            register.modified = True

        if self.value is not None:
            result += self.value._fuckUp(compiler)

        result += '%s[' % MovePointer(self.fromRegister._finalIndex())._fuckUp(compiler)
        for register in self.toRegisters:
            #move to dest, incremement
            result += '%s+' % MovePointer(register._finalIndex())._fuckUp(compiler)

        #move from last to beginning
        result += '%s-]' % MovePointer(self.fromRegister._finalIndex())._fuckUp(compiler)
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

    def _fuckUp(self, compiler):
        curPointer = compiler.pointer
        return '%s%s' % (Move(self.fromRegister, [self.temp, self.toRegister])._fuckUp(compiler),
                         Move(self.temp, [self.fromRegister])._fuckUp(compiler))
        self.toRegister.modified = True
        self.temp.modified = True

#store a pointer to a string into a register
class String:
    _command = 'string'

    string = None
    destRegister = None
    temps = []
    name = None
    values = []

    def __init__(self, name, string):
        self.string = string[1:-1] #get rid of 's
        self.name = name
        self.temps = [TempRegister() for x in xrange(len(self.string)+1)] #extra register makes a null byte at the end
        String.strings[self.name] = None

    def _fuckUp(self, compiler):
        curPointer = compiler.pointer
        String.strings[self.name] = (self.temps[0]._finalIndex(), len(self.string))
        #this is a hax to use less operations and not make the code a massive blob of nothing
        result = MovePointer(self.temps[0]._finalIndex())._fuckUp(compiler)
        for i in xrange(len(self.string)):
            result += '>'+'+' * (ord(self.string[i])/10)
            result += '[<++++++++++>-]<%s>' % ('+'*(ord(self.string[i])%10))
        result += '[-]'
        curPointer.move(int(curPointer)+len(self.string))
        return result

String.strings = {}

#TODO: print integer values of registers

class Print:
    _command = 'print'
    name = None

    def __init__(self, name):
        self.name = name
        if name not in String.strings:
            raise Exception('String %s does not exist' % self.name)

    def _fuckUp(self, compiler):
        curPointer = compiler.pointer
        #move to index of string
        result = MovePointer(String.strings[self.name][0])._fuckUp(compiler)
        result += '[,>]'
        curPointer.move(int(curPointer)+String.strings[self.name][1])
        return result

class Printr:
    def __init__(self, *args):
        pass
    def _fuckUp(self, *args):
        return '?'

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
                'multiply': Multiply,
                'printr': Printr,
                'string': String,
                'print': Print}

    #commands are [command, args...]
    def compile(self):
        result = ''
        commands = []
        registers = defaultdict(Register)

        for line in self.proggy.split('\n'):
            if not line:
                continue
            try:
                command, args = line.split(' ', 1)
            except ValueError:
                command, args = line, ' '
            args = args.split(',')
            for i in xrange(len(args)):
                args[i] = args[i].strip()
                try:
                    number = int(args[i])
                    args[i] = TempRegister()
                    commands.append(Value(args[i], number))
                except ValueError:
                    try:
                        if args[i][0] == 'r':
                            args[i] = registers[int(args[i][1:])]
                    except (ValueError, IndexError):
                        pass

            if command not in self.commands:
                print 'Unsupported command: \'%s\'' % command
            else:
                #print 'Command', command, args
                commands.append(self.commands[command](*args))

        self.resolveRegisters()

        Register.disabled = True
        for command in commands:
            result += command._fuckUp(self)

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
    outputfile.write('\n')
    outputfile.close()
