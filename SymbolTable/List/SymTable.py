from Error import *
from typing import List
import re

class Symbol:
    def __init__(self, iden: str, typ: type):
        self.iden = iden
        self.typ = typ
    
    def __str__(self):
        return "Symbol({},{})".format(self.iden, self.typ)

class SymbolTable:
    def __init__(self):
        self.symbolList: List[List[Symbol]] = [[]]
        self.stage = 0

    def run(self):
        n = int(input())
        list_ins: List[str] = []
        for i in range(n):
            list_ins += [input()]
        
        for i in range(len(list_ins)):
            ins = list_ins[i]
            for idx in range(len(ins) - 1):
                if ins[idx] == ' ' and ins[idx + 1] == ' ':
                    raise InvalidInstruction(ins)
            if ins[-1] == ' ':
                raise InvalidInstruction(ins)
            
            ins_list = ins.split(sep = ' ')
            if ins_list[0] not in ['PRINT', 'RPRINT', 'INSERT', 'LOOKUP', 'ASSIGN', 'BEGIN', 'END']:
                raise InvalidInstruction(ins)
            
            if ins_list[0] == 'INSERT':
                if len(ins_list) != 3:
                    raise InvalidInstruction(ins)
                
                if not re.fullmatch("^[a-z][a-zA-Z0-9_]*", ins_list[1]) or re.fullmatch("number|string", ins_list[1]):
                    raise InvalidInstruction(ins)
                
                if ins_list[2] not in ['number', 'string']:
                    raise InvalidInstruction(ins)
                
                sym = Symbol(ins_list[1], ins_list[2])
                
                for symbol in self.symbolList[self.stage]:
                    if symbol.iden == ins_list[1]:
                        raise Redeclared(ins)
                    
                self.symbolList[self.stage] += [sym]
                print('success')

            elif ins_list[0] == 'ASSIGN':
                if len(ins_list) != 3:
                    raise InvalidInstruction(ins)
                
                if not re.fullmatch("^[a-z][a-zA-Z0-9_]*", ins_list[1]):
                    raise InvalidInstruction(ins)

                flag = False
                rev = self.symbolList[::-1]
                for symList in rev:
                    for symbol in symList:
                        if symbol.iden == ins_list[1]:
                            flag = True
                            if re.fullmatch("[0-9]+", ins_list[2]):
                                if symbol.typ != 'int':
                                    raise TypeMismatch(ins)
                            elif re.fullmatch("['][a-zA-Z0-9 ]*[']", ins_list[2]):
                                if symbol.typ != 'string':
                                    raise TypeMismatch(ins)
                            else:
                                if not re.fullmatch("^[a-z][a-zA-Z0-9_]*", ins_list[2]):
                                    raise InvalidInstruction(ins)
                                
                                nextFlag = False
                                for symList1 in rev:
                                    for symbol1 in symList1:
                                        if symbol1.iden == ins_list[2]:
                                            nextFlag = True
                                            if symbol1.typ != symbol.typ:
                                                raise TypeMismatch(ins)
                                            break
                                    if nextFlag:
                                        break
                                if not nextFlag:
                                    raise Undeclared(ins_list[2])
                            break
                    if flag:
                        break
                    
                if not flag:
                    raise Undeclared(ins_list[1])
                print('success')

            elif ins_list[0] == 'BEGIN':
                if len(ins_list) != 1:
                    raise InvalidInstruction(ins)
                
                self.stage += 1
                self.symbolList += [[]]
            
            elif ins_list[0] == 'END':
                if len(ins_list) != 1:
                    raise InvalidInstruction(ins)
                
                self.stage -= 1
                self.symbolList = self.symbolList[:-1]
                if self.stage < 0:
                    raise UnknownBlock()
            
            elif ins_list[0] == 'LOOKUP':
                if len(ins_list) != 2:
                    raise InvalidInstruction(ins)
                
                if not re.fullmatch("^[a-z][a-zA-Z0-9_]*", ins_list[1]):
                    raise InvalidInstruction(ins)

                flag = False
                for idx in range(self.stage, -1, -1):
                    for idx1 in range(len(self.symbolList[idx])):
                        if self.symbolList[idx][idx1].iden == ins_list[1]:
                            print(idx)
                            flag = True
                            break
                    if flag:
                        break
                if not flag:
                    raise Undeclared(ins_list[1])
            
            elif ins_list[0] == 'PRINT':
                if len(ins_list) != 1:
                    raise InvalidInstruction(ins)

                res = []
                for i in range(self.stage + 1):
                    for symbol in self.symbolList[i]:
                        for idx, value in enumerate(res):
                            if value[0] == symbol.iden:
                                res.pop(idx)
                                break
                        res += [(symbol.iden, i)]
                
                result = "{}".format(" ".join([value[0] + '//' + str(value[1]) for value in res]))
                print(result)

            else:
                if len(ins_list) != 1:
                    raise InvalidInstruction(ins)

                res = []
                for i in range(self.stage, -1, -1):
                    rev = self.symbolList[i][::-1]
                    for symbol in rev:
                        flag = False
                        for idx, value in enumerate(res):
                            if value[0] == symbol.iden:
                                flag = True
                                break
                        
                        if not flag:
                            res += [(symbol.iden, i)]
                
                result = "{}".format(" ".join([value[0] + '//' + str(value[1]) for value in res]))
                print(result)

        if self.stage > 0:
            raise UnclosedBlock(self.stage)
                    
