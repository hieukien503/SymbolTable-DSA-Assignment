class SymbolTableError(Exception):
    pass

class Undeclared(SymbolTableError):
    def __init__(self, msg: str):
        self.msg = msg
    
    def __str__(self):
        return f"Undeclared: {self.msg}"


class Redeclared(SymbolTableError):
    def __init__(self, msg: str):
        self.msg = msg
    
    def __str__(self):
        return f"Redeclared: {self.msg}"


class TypeMismatch(SymbolTableError):
    def __init__(self, msg: str):
        self.msg = msg
    
    def __str__(self):
        return f"TypeMismatch: {self.msg}"


class UnclosedBlock(SymbolTableError):
    def __init__(self, block: int):
        self.block = block
    
    def __str__(self):
        return f"UnclosedBlock: {self.block}"


class UnknownBlock(SymbolTableError):
    def __str__(self):
        return f"UnknownBlock"


class InvalidInstruction(SymbolTableError):
    def __init__(self, msg: str):
        self.msg = msg
    
    def __str__(self):
        return f"InvalidInstruction: {self.msg}"