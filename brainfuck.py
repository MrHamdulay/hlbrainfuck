#!/usr/bin/env python
import sys

class BrainfuckInterpreter:
    symbols = '><+-[].,'
    registers = None
    loopStack = None
    pointer = 0

    instructionPos = 0
    #ALl the instructions fed into the program
    instructions = ''


    def __init__(self):
        self.registers = [0] * 1000
        self.loopStack = []

    def shiftRight(self):
        self.pointer += 1

    def shiftLeft(self):
        self.pointer -= 1

    def increment(self):
        self.registers[self.pointer] += 1

    def decrement(self):
        self.registers[self.pointer] -= 1

    def beginLoop(self):
        self.loopStack.append(self.instructionPos)

    def endLoop(self):
        if self.registers[self.pointer] != 0:
            self.instructionPos = self.loopStack[-1]
        else:
            self.loopStack.pop()

    def getChar(self):
        self.registers[self.pointer] = ord(sys.stdin.read()[0])

    def putChar(self):
        print 'done',chr(self.registers[self.pointer])

    commands = [shiftRight, shiftLeft, increment, decrement, beginLoop, endLoop, getChar, putChar]

    def run(self, proggy):
        for char in proggy:
            c = self.symbols.find(char)
            if c == -1:
                continue
            self.commands[c](self)

if __name__ == '__main__':
    interpreter = BrainfuckInterpreter()

    if len(sys.argv) > 1:
        inp = open(sys.argv[1], 'r')
    else:
        print 'python ./brainfuck.py [filename]'
        sys.exit(1)

    for line in inp:
        interpreter.run(line)
