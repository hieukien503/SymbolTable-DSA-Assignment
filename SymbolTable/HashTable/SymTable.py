from Error import *
from typing import List
import re

class Symbol:
    def __init__(self, iden: str, typ: str, stage: int, numParam: int = -1):
        self.iden = iden
        self.typ = typ
        self.stage = stage
        self.numParam = numParam
    
    def __str__(self):
        return "{}//{}".format(self.iden, self.stage)

def makeKey(iden: str, stage: int) -> int:
    res: str = "{}{}".format(str(stage), "".join([str(ord(ch) - 48) for ch in iden]))
    return int(res)

def LinearProbing(key: int, m: int, i: int, c1: int, c2: int = 0):
    def h(key: int) -> int:
        return key % m
    return (h(key) + c1 * i) % m

def QuadraticProbing(key: int, m: int, i: int, c1: int, c2: int = 0):
    def h(key: int) -> int:
        return key % m
    return (h(key) + c1 * i + c2 * i * i) % m

def DoubleProbing(key: int, m: int, i: int, c1: int, c2: int = 0):
    def h1(key: int) -> int:
        return key % m
    def h2(key: int) -> int:
        return 1 + (key % (m - 2))
    return (h1(key) + c1 * i * h2(key)) % m 

class SymbolTable:
    def __init__(self):
        self.stage = 0
        self.symbolList: List[Symbol] = []
        self.probFunc = None
        self.size = 0
        self.c1 = 0
        self.c2 = 0

    def search(self, iden: str):
        for i in range (self.stage, -1, -1):
            for j in range(self.size):
                idx = self.probFunc(makeKey(iden, self.stage), self.size, j, self.c1, self.c2)
                if self.symbolList[idx].iden == iden and self.symbolList[idx].stage <= self.stage:
                    return self.symbolList[idx], j, idx
        return None

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
            if ins_list[0] not in ['PRINT', 'INSERT', 'LOOKUP', 'ASSIGN', 'BEGIN', 'END', 'LINEAR', 'QUADRATIC', 'DOUBLE', 'CALL']:
                raise InvalidInstruction(ins)
            
            if ins_list[0] == 'LINEAR':
                if len(ins_list) != 3:
                    raise InvalidInstruction(ins)
                
                self.probFunc = LinearProbing
                self.size = int(ins_list[1])
                self.c1 = int(ins_list[2])
                self.symbolList = [Symbol("", "", 0)] * self.size
            
            elif ins_list[0] == 'QUADRATIC':
                if len(ins_list) != 4:
                    raise InvalidInstruction(ins)
                
                self.probFunc = QuadraticProbing
                self.size = int(ins_list[1])
                self.c1 = int(ins_list[2])
                self.c2 = int(ins_list[3])
                self.symbolList = [Symbol("", "", 0)] * self.size
            
            elif ins_list[0] == 'DOUBLE':
                if len(ins_list) != 3:
                    raise InvalidInstruction(ins)
                
                self.probFunc = DoubleProbing
                self.size = int(ins_list[1])
                self.c1 = int(ins_list[2])
                self.symbolList = [Symbol("", "", 0)] * self.size
            
            elif ins_list[0] == 'INSERT':
                if len(ins_list) not in [2, 3]:
                    raise InvalidInstruction(ins)
                
                if not re.fullmatch("[a-z][a-zA-Z0-9_]*", ins_list[1]) or re.fullmatch("number|string", ins_list[1]):
                    raise InvalidInstruction(ins)
                
                sym: Symbol | None = None
                if len(ins_list) == 2:
                    sym = Symbol(ins_list[1], "", self.stage)
                    
                else:
                    if self.stage != 0:
                        raise InvalidInstruction(ins)
                    if not re.fullmatch("[0-9]+", ins_list[2]):
                        raise InvalidInstruction(ins)
                    sym = Symbol(ins_list[1], "", self.stage, int(ins_list[2]))
                
                flag = False
                for i in range(self.size):
                    idx = self.probFunc(makeKey(ins_list[1], self.stage), self.size, i, self.c1, self.c2)
                    if self.symbolList[idx].iden == sym.iden and self.symbolList[idx].stage == sym.stage:
                        raise Redeclared(ins_list[1])
                    if self.symbolList[idx].iden == "":
                        self.symbolList[idx] = sym
                        flag = True
                        print(i)
                        break
                if not flag:
                    raise Overflow(ins)

            elif ins_list[0] == 'ASSIGN':
                sum_slot: int = 0
                before_idx: int = -1
                if len(ins_list) != 3:
                    raise InvalidInstruction(ins)
                
                rhs_type: str = ""
                if re.fullmatch("[0-9]+", ins_list[2]):
                    rhs_type = "number"

                elif re.fullmatch("^['][a-zA-Z0-9 ]*[']$", ins_list[2]):
                    rhs_type = "string"
                
                elif re.fullmatch("[a-z][a-zA-Z0-9_]*", ins_list[2]):
                    tmp = self.search(ins_list[2])

                    if tmp is not None:
                        rhs_type = tmp[0].typ
                        sum_slot += tmp[1]
                        before_idx = tmp[2]
                    else:
                        raise Undeclared(ins_list[2])
                else:
                    param_regex = "[a-zA-Z0-9 ']+"
                    if not re.fullmatch("([a-z][a-zA-Z0-9_]*)[(](" + param_regex + "([,]" + param_regex + ")*)?[)]", ins_list[2]):
                        raise InvalidInstruction(ins)
                    
                    idx = ins_list[2].find('(')
                    iden = ins_list[2][:idx]
                    tmp = self.search(iden)
                    if tmp is None:
                        raise Undeclared(iden)
                    
                    sum_slot += tmp[1]
                    before_idx = tmp[2]
                    arg_part = ins_list[2][idx:][1:-1].split(',')
                    func_part, param_list = [], []
                    if tmp[0].typ != "":
                        func_part = tmp[0].typ.split('->')
                        param_list = func_part[0][1:-1].split(',')

                    if len(arg_part) != tmp[0].numParam:
                        raise TypeMismatch(ins)
                    
                    para_list: List[str] = []
                    for idx, args in enumerate(arg_part):
                        if not re.fullmatch("[0-9]+", args) and not re.fullmatch("[\'][a-zA-Z0-9 ]*[\']", args) and not re.fullmatch("[a-z][a-zA-Z0-9_]*", args):
                            raise InvalidInstruction(ins)
                        if re.fullmatch("[0-9]+", args):
                            if param_list != [] and param_list[idx] != 'number':
                                raise TypeMismatch(ins)
                            para_list += ['number']
                        elif re.fullmatch("['][a-zA-Z0-9 ]*[']", args):
                            if param_list != [] and param_list[idx] != 'string':
                                raise TypeMismatch(ins)
                            para_list += ['string']
                        else:
                            temp = self.search(args)
                            if temp is None:
                                raise Undeclared(args)
                            if temp[0].typ == "":
                                raise TypeCannotBeInferred(ins)
                        
                            if param_list != [] and temp[0].typ != param_list[idx]:
                                raise TypeMismatch(ins)
                        
                            sum_slot += temp[1]
                            para_list += [temp[0].typ]
                    
                    rhs_type = func_part[1] if func_part != [] else tmp[0].typ

                if not re.fullmatch("^[a-z][a-zA-Z0-9_]*", ins_list[1]):
                    raise InvalidInstruction(ins)
                
                tmp = self.search(ins_list[1])
                if tmp is None:
                    raise Undeclared(ins_list[1])
                
                if rhs_type == "" and tmp[0].typ == "":
                    raise TypeCannotBeInferred(ins)
                
                if rhs_type == "void":
                    raise TypeMismatch(ins)
                
                sum_slot += tmp[1]
                if rhs_type != "" and tmp[0].typ == "":
                    self.symbolList[tmp[2]].typ = rhs_type
                
                elif tmp[0].typ != "" and rhs_type == "":
                    if not re.fullmatch("([a-z][a-zA-Z0-9_]*)[(](" + param_regex + "([,]" + param_regex + ")*)?[)]", ins_list[2]):
                        self.symbolList[before_idx].typ = tmp[0].typ
                    else:
                        func_type = "({})->{}".format(",".join([typ for typ in para_list]), tmp[0].typ)
                        self.symbolList[before_idx].typ = func_type
                else:
                    if rhs_type != tmp[0].typ:
                        raise TypeMismatch(ins)
                    
                print(sum_slot)
            
            elif ins_list[0] == 'CALL':
                sum_slot, before_idx = 0, 0
                if len(ins_list) != 2:
                    raise InvalidInstruction(ins)
                param_regex = "[a-zA-Z0-9 ']+"
                if not re.fullmatch("([a-z][a-zA-Z0-9_]*)[(](" + param_regex + "([,]" + param_regex + ")*)?[)]", ins_list[1]):
                    raise InvalidInstruction(ins)
                
                idx = ins_list[1].find('(')
                iden = ins_list[1][:idx]
                tmp = self.search(iden)
                if tmp is None:
                    raise Undeclared(iden)
                
                sum_slot += tmp[1]
                before_idx = tmp[2]
                arg_part = ins_list[1][idx:][1:-1].split(',')
                func_part, param_list = [], []
                if tmp[0].typ != "":
                    func_part = tmp[0].typ.split('->')
                    param_list = func_part[0][1:-1].split(',')

                if len(arg_part) != tmp[0].numParam:
                    raise TypeMismatch(ins)
                    
                para_list: List[str] = []
                for idx, args in enumerate(arg_part):
                    if not re.fullmatch("[0-9]+", args) and not re.fullmatch("[\'][a-zA-Z0-9 ]*[\']", args) and not re.fullmatch("[a-z][a-zA-Z0-9_]*", args):
                        raise InvalidInstruction(ins)
                    if re.fullmatch("[0-9]+", args):
                        if param_list != [] and param_list[idx] != 'number':
                            raise TypeMismatch(ins)
                        para_list += ['number']
                    elif re.fullmatch("['][a-zA-Z0-9 ]*[']", args):
                        if param_list != [] and param_list[idx] != 'string':
                            raise TypeMismatch(ins)
                        para_list += ['string']
                    else:
                        temp = self.search(args)
                        if temp is None:
                            raise Undeclared(args)
                        if temp[0].typ == "":
                            raise TypeCannotBeInferred(ins)
                        
                        if param_list != [] and temp[0].typ != param_list[idx]:
                            raise TypeMismatch(ins)
                        
                        sum_slot += temp[1]
                        para_list += [temp[0].typ]
                    
                func_type = "({})->{}".format(",".join([typ for typ in para_list]), "void")
                self.symbolList[before_idx].typ = func_type
                print(sum_slot)

            elif ins_list[0] == 'BEGIN':
                if len(ins_list) != 1:
                    raise InvalidInstruction(ins)
                self.stage += 1
            
            elif ins_list[0] == 'END':
                if len(ins_list) != 1:
                    raise InvalidInstruction(ins)
                
                for idx, symbol in enumerate(self.symbolList):
                    if symbol.stage == self.stage:
                        self.symbolList[idx] = Symbol("", "", 0)

                self.stage -= 1
                if self.stage < 0:
                    raise UnknownBlock()
            
            elif ins_list[0] == 'LOOKUP':
                if len(ins_list) != 2:
                    raise InvalidInstruction(ins)
                
                if not re.fullmatch("^[a-z][a-zA-Z0-9_]*", ins_list[1]):
                    raise InvalidInstruction(ins)

                tmp = self.search(ins_list[1])
                if tmp is None:
                    raise Undeclared(ins_list[1])
                else:
                    print(tmp[2])
            
            elif ins_list[0] == 'PRINT':
                res = []
                for idx, value in enumerate(self.symbolList):
                    if value.iden != "":
                        res += ["{} {}".format(idx, str(value))]
                print(";".join(res)) 

        if self.stage > 0:
            raise UnclosedBlock(self.stage)
                    
