# CS 5300 Project 1 SQL -> relational algebra
# Luka Ivicevic and David Tutt
# Notes:
#   -   Trouble matching some single quoted strings, if test input is copy and pasted from website, 
#       the single quotes used are unicode right/left single quotation mark, if typed from my keyboard,
#       it is unicode apostrophe.
#
#
#

# Imports
from pyparsing import Literal, CaselessLiteral, Word, delimitedList, Optional, \
    Combine, Group, alphas, nums, alphanums, ParseException, Forward, oneOf, quotedString, \
    ZeroOrMore, restOfLine, Keyword, upcaseTokens

# Define SQL tokens
selectStmt = Forward()
SELECT = Keyword("select", caseless=True)
FROM = Keyword("from", caseless=True)
WHERE = Keyword("where", caseless=True)
AS = Keyword("as", caseless=True)
UNION = Keyword("union", caseless=True)
INTERSECT = Keyword("intersect", caseless=True)
EXCEPT = Keyword("except", caseless=True)
COUNT = Keyword("count", caseless=True)
MAX = Keyword("max", caseless=True)
AVG = Keyword("avg", caseless=True)
SUM = Keyword("sum", caseless=True)

ident = Word( alphas, alphanums + "_$" ).setName("identifier")
columnName = ( delimitedList( ident, ".", combine=True ) ).setName("column name").addParseAction(upcaseTokens)
columnNameList = Group( delimitedList( columnName ))
tableName = ( delimitedList( ident, ".", combine=True ) ).setName("table name").addParseAction(upcaseTokens)
tableNameAs = ( delimitedList( ident + " " + AS + " " + ident, ".", combine=True ) ).setName("table name").addParseAction(upcaseTokens)
tableNameList = Group( delimitedList( tableName ) )
tableNameAsList = Group( delimitedList( tableNameAs ) )

whereExpression = Forward()
and_ = Keyword("and", caseless=True)
or_ = Keyword("or", caseless=True)
in_ = Keyword("in", caseless=True)
GROUP_BY = Keyword("group by", caseless=True)
HAVING = Keyword("having", caseless=True)
CONTAINS = Keyword("contains", caseless=True)

E = CaselessLiteral("E")
binop = oneOf("= != < > >= <= eq ne lt le gt ge", caseless=True)
arithSign = Word("+-",exact=1)
realNum = Combine( Optional(arithSign) + ( Word( nums ) + "." + Optional( Word(nums) )  |
                                                         ( "." + Word(nums) ) ) + 
            Optional( E + Optional(arithSign) + Word(nums) ) )
intNum = Combine( Optional(arithSign) + Word( nums ) + 
            Optional( E + Optional("+") + Word(nums) ) )

columnRval = realNum | intNum | quotedString | columnName
whereCondition = Group(
    ( columnName + binop + columnRval ) |
    ( columnName + in_ + "(" + delimitedList( columnRval ) + ")" ) |
    ( columnName + in_ + "(" + selectStmt + ")" ) |
    ( "(" + whereExpression + ")" )
    )
whereExpression << whereCondition + ZeroOrMore( ( and_ | or_ ) + whereExpression ) 

# Define the SQL grammar
selectStmt <<= (SELECT + ('*' | columnNameList)("columns") + \
                FROM + (tableNameAsList | tableNameList)( "tables" ) + \
                Optional(Group(WHERE + whereExpression), "")("where")) + \
                Optional((UNION + selectStmt)("union") | (INTERSECT + selectStmt)("intersect") | (EXCEPT + selectStmt)("except")) 

SQLParser = selectStmt | ("(" + selectStmt + ")")

# Tests
if __name__ == "__main__":
    test = "SELECT S.sname FROM Sailors AS S where S.sid IN ((SELECT R.sid FROM Reserve AS R, Boats AS B WHERE R.bid = B.bid AND B.color = 'red') INTERSECT (SELECT R2.sid FROM Reserve AS R2, Boats AS B2 WHERE R2.bid = B2.bid AND B2.color = 'green'))"
    try:
        print(test, "\n-----\n", SQLParser.parseString(test))
    except Exception as e:
        print("Syntax Error parsing: " + test)
        print(e)