#!/usr/bin/env python2
import sys

class BrainfuckInterpreter:
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
        print 'done',self.registers[self.pointer]

    symbols = '><+-[].,'
    commands = [shiftRight, shiftLeft, increment, decrement, beginLoop, endLoop, getChar, putChar]

    def execChar(self, command):
        if command in self.symbols:
            self.commands[self.symbols.find(command)](self)

    def run(self, proggy):
        while self.instructionPos < len(proggy):
            self.execChar(proggy[self.instructionPos])
            self.instructionPos += 1


if __name__ == '__main__':
    interpreter = BrainfuckInterpreter()

    if len(sys.argv) > 1:
        inp = open(sys.argv[1], 'r')
    else:
        print 'python ./brainfuck.py [filename]'
        sys.exit(1)

    for line in inp:
        interpreter.run(line)
