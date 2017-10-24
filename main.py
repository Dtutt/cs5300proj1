
import parser
loop=1



while loop:
    print("1. Run Query")
    print("2. End")
    choice = input("enter number of option")
    if choice=='1':
        SQL=input("Enter SQL query")
        SQLparse=parser(SQL)
        RAstr=SQL_RA(SQLparse)
        tree=RA_Tree(RAstr)
    elif choice=='2':
        loop=0


