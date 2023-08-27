from SymTable import SymbolTable
from Error import *

def main():
    symTable = SymbolTable()
    try:
        symTable.run()
    except SymbolTableError as e:
        print(str(e))


if __name__ == '__main__':
    main()