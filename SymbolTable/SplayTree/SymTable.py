from Error import *
from typing import List
import re

class Symbol:
    def __init__(self, iden: str, typ: str, isStatic: bool, stage: int):
        self.iden = iden
        self.typ = typ
        self.isStatic = isStatic
        self.stage = 0 if isStatic else stage
    
    def __str__(self):
        return "{}//{}".format(self.iden, self.stage)

def compare(sym1: Symbol, sym2: Symbol) -> int:
    if sym1.stage < sym2.stage:
        return -1
    
    if sym2.stage < sym1.stage:
        return 1
    return -1 if sym1.iden < sym2.iden else (1 if sym2.iden < sym1.iden else 0)

class Node:
    def __init__(self, sym: Symbol):
        self.sym = sym
        self.left: Node = None
        self.right: Node = None
        self.parent: Node = None

class SplayTree:
    def __init__(self):
        self.root: Node | None = None
        self.numSplay = self.numCompare = 0
    
    def __leftRotate(self, x: Node):
        y: Node = x.right
        x.right = y.left
        if y.left is not None:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def __rightRotate(self, x: Node):
        y: Node = x.left
        x.left = y.right
        if y.right is not None:
            y.right.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y
    
    def __splay(self, x: Node):
        while x.parent is not None:
            if x.parent.parent is None:
                if x == x.parent.left:
                    self.__rightRotate(x.parent)
                else:
                    self.__leftRotate(x.parent)
            elif x == x.parent.left and x.parent == x.parent.parent.left:
                self.__rightRotate(x.parent.parent)
                self.__rightRotate(x.parent)
            elif x == x.parent.right and x.parent == x.parent.parent.right:
                self.__leftRotate(x.parent.parent)
                self.__leftRotate(x.parent)
            elif x == x.parent.left and x.parent == x.parent.parent.right:
                self.__rightRotate(x.parent)
                self.__leftRotate(x.parent)
            else:
                self.__leftRotate(x.parent)
                self.__rightRotate(x.parent)
    
    def __searchHelper(self, root: Node, iden: str, stage: int) -> Node:
        if root is None:
            return None
        
        if root.sym.iden == iden and root.sym.stage == stage:
            self.numCompare += 1
            return root
        
        if compare(root.sym, Symbol(iden, "", False, stage)) == 1:
            self.numCompare += 1
            return self.__searchHelper(root.left, iden, stage)
        
        else:
            self.numCompare += 1
            return self.__searchHelper(root.right, iden, stage)
    
    def __findMax(self, x: Node) -> Node:
        while x.right is not None:
            x = x.right
        return x
    
    def __join(self, s: Node, t: Node):
        if s is None:
            return t
        x: Node = self.__findMax(s)
        self.__splay(x)
        x.right = t
        if t is not None:
            t.parent = x
        return x
    
    def __delete_helper(self, root: Node, sym: Symbol):
        x, temp = None, root
        while temp is not None:
            if compare(temp.sym, sym) == 0:
                x = temp
                break
            if compare(temp.sym, sym) == -1:
                temp = temp.right
            else:
                temp = temp.left
        if x is None:
            return
        
        self.__splay(x)
        s, t = None, None
        if x.right is not None:
            t = x.right
            t.parent = None
        else:
            t = None
        s = x
        s.right = None
        x = None

        self.root = self.__join(s.left, t)
        s = None
    
    def __printTreeHelper(self, root: Node, res: str = "") -> str:
        if root is None:
            return res
        res += (str(root.sym) + ' ')
        res = self.__printTreeHelper(root.left, res)
        res = self.__printTreeHelper(root.right, res)
        return res
    
    def insert(self, sym: Symbol, msg: str):
        tmp, x, y = Node(sym), self.root, None
        while x is not None:
            y = x
            if compare(x.sym, tmp.sym) == -1:
                x = x.right
            elif compare(x.sym, tmp.sym) == 1:
                x = x.left
            else:
                raise Redeclared(msg)
            self.numCompare += 1
        tmp.parent = y
        if y is None:
            self.root = tmp
            return
        elif compare(tmp.sym, y.sym) == -1:
            y.left = tmp
        else:
            y.right = tmp

        if tmp != self.root:
            self.__splay(tmp)
            self.numSplay += 1
    
    def search(self, iden: str, stage: int):
        for idx in range(stage, -1, -1):
            tmp: Node = self.__searchHelper(self.root, iden, idx)
            if tmp is not None:
                if tmp != self.root:
                    self.__splay(tmp)
                    self.numSplay += 1
                return tmp
        return None
    
    def remove(self, sym: Symbol):
        self.__delete_helper(self.root, sym)
    
    def __str__(self):
        res = self.__printTreeHelper(self.root)
        return res[:-1]

class SymbolTable:
    def __init__(self):
        self.symbolTree = SplayTree()
        self.stage = 0
        self.symbolList: List[List[Symbol]] = [[]]

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
            if ins_list[0] not in ['PRINT', 'INSERT', 'LOOKUP', 'ASSIGN', 'BEGIN', 'END']:
                raise InvalidInstruction(ins)
            
            if ins_list[0] == 'INSERT':
                if len(ins_list) != 4:
                    raise InvalidInstruction(ins)
                
                if not re.fullmatch("[a-z][a-zA-Z0-9_]*", ins_list[1]) or re.fullmatch("number|string|false|true", ins_list[1]):
                    raise InvalidInstruction(ins)
                
                if ins_list[2] not in ['number', 'string']:
                    if not re.fullmatch("[(]((number|string)([,](number|string))*)?[)]->(number|string)", ins_list[2]) or self.stage != 0:
                        raise InvalidInstruction(ins)
                
                if not re.fullmatch("true|false", ins_list[3]):
                    raise InvalidInstruction(ins)
                
                isStatic: bool = True if ins_list[3] == "true" else False
                sym = Symbol(ins_list[1], ins_list[2], isStatic, self.stage)
                
                self.symbolTree.numCompare = self.symbolTree.numSplay = 0
                self.symbolTree.insert(sym, ins)
                if isStatic:
                    self.symbolList[0] += [sym]
                else:
                    self.symbolList[self.stage] += [sym]
                print(self.symbolTree.numCompare, self.symbolTree.numSplay)

            elif ins_list[0] == 'ASSIGN':
                self.symbolTree.numCompare = self.symbolTree.numSplay = 0
                if len(ins_list) != 3:
                    raise InvalidInstruction(ins)
                
                rhs_type: str = ""
                if re.fullmatch("[0-9]+", ins_list[2]):
                    rhs_type = "number"

                elif re.fullmatch("^['][a-zA-Z0-9 ][']$", ins_list[2]):
                    rhs_type = "string"
                
                elif re.fullmatch("[a-z][a-zA-Z0-9_]*", ins_list[2]):
                    tmp = self.symbolTree.search(ins_list[2], self.stage)
                    if tmp is not None:
                        rhs_type = tmp.sym.typ
                    else:
                        raise Undeclared(ins_list[2])
                else:
                    param_regex = "[a-zA-Z0-9 ']+"
                    if not re.fullmatch("([a-z][a-zA-Z0-9_]*)[(](" + param_regex + "([,]" + param_regex + ")*)?[)]", ins_list[2]):
                        raise InvalidInstruction(ins)
                    
                    idx = ins_list[2].find('(')
                    iden = ins_list[2][:idx]
                    tmp = self.symbolTree.search(iden, 0)
                    if tmp is None:
                        raise Undeclared(iden)
                    
                    arg_part = ins_list[2][idx:][1:-1].split(',')
                    func_part = tmp.sym.typ.split('->')
                    param_list = func_part[0][1:-1].split(',')
                    if len(arg_part) != len(param_list):
                        raise TypeMismatch(ins)
                    
                    for idx, args in enumerate(arg_part):
                        if not re.fullmatch("[0-9]+", args) and not re.fullmatch("[\'][a-zA-Z0-9 ]*[\']", args) and not re.fullmatch("[a-z][a-zA-Z0-9_]*", args):
                            raise InvalidInstruction(ins)
                        if re.fullmatch("[0-9]+", args):
                            if param_list[idx] != 'number':
                                raise TypeMismatch(ins)
                        elif re.fullmatch("['][a-zA-Z0-9 ]*[']", args):
                            if param_list[idx] != 'string':
                                raise TypeMismatch(ins)
                        else:
                            temp = self.symbolTree.search(args, self.stage)
                            if temp is None:
                                raise Undeclared(args)
                            if temp.sym.typ != param_list[idx]:
                                raise TypeMismatch(ins)
                    
                    rhs_type = func_part[1]

                
                if not re.fullmatch("^[a-z][a-zA-Z0-9_]*", ins_list[1]):
                    raise InvalidInstruction(ins)
                
                tmp = self.symbolTree.search(ins_list[1], self.stage)
                if tmp is None:
                    raise Undeclared(ins_list[1])
                
                if tmp.sym.typ != rhs_type:
                    raise TypeMismatch(ins)
                
                print(self.symbolTree.numCompare, self.symbolTree.numSplay)

            elif ins_list[0] == 'BEGIN':
                if len(ins_list) != 1:
                    raise InvalidInstruction(ins)
                self.symbolList += [[]]
                self.stage += 1
            
            elif ins_list[0] == 'END':
                if len(ins_list) != 1:
                    raise InvalidInstruction(ins)
                
                for symbol in self.symbolList[self.stage]:
                    self.symbolTree.remove(symbol)

                self.symbolList = self.symbolList[:-1]
                self.stage -= 1
                if self.stage < 0:
                    raise UnknownBlock()
            
            elif ins_list[0] == 'LOOKUP':
                if len(ins_list) != 2:
                    raise InvalidInstruction(ins)
                
                if not re.fullmatch("^[a-z][a-zA-Z0-9_]*", ins_list[1]):
                    raise InvalidInstruction(ins)

                tmp = self.symbolTree.search(ins_list[1], self.stage)
                if tmp is None:
                    raise Undeclared(ins_list[1])
                else:
                    print(tmp.sym.stage)
            
            elif ins_list[0] == 'PRINT':
                print(self.symbolTree)

        if self.stage > 0:
            raise UnclosedBlock(self.stage)
                    
