# CS 5300 Project 1 SQL -> relational algebra
# Luka Ivicevic and David Tutt
# Notes:
#   -   Trouble matching some single quoted strings, if test input is copy and pasted from website,
#       the single quotes used are unicode right/left single quotation mark, if typed from my keyboard,
#       it is unicode apostrophe.
#
#

# Imports
import sqlparser
loop=True



while loop:
    print("1. Run Query")
    print("2. End")
    #choice = input("enter number of option")
    choice='1'
    if choice=='1':
        #SQL=input("Enter SQL query")
        SQL="SELECT sid, sname as s, max(rating), E FROM Sailors as T, Boats WHERE count(sid) = 2 and S2.rating = 10 and sid = 4 GROUP BY sid Having count(d) > 5 or max(R) = 5"
        RAstr=sqlparser.sqlparse(SQL)
        loop=False
    elif choice=='2':
        loop=False


