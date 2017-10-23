# CS 5300 Project 1 SQL -> relational algebra
# Luka Ivicevic and David Tutt

from pyparsing import *

# Define SQL tokens
selectStmt = Forward()
SELECT = Keyword("select", caseless=True)
FROM = Keyword("from", caseless=True)
WHERE = Keyword("where", caseless=True)
AS = Keyword("as", caseless=True)
UNION = Keyword("union", caseless=True)
INTERSECT = Keyword("intersect", caseless=True)
COUNT = Keyword("count", caseless=True)
MAX = Keyword("max", caseless=True)
AVG = Keyword("avg", caseless=True)
SUM = Keyword("sum", caseless=True)

ident = Word(alphas, alphanums + "_$").setName("Identifier")
columnName = (delimitedList(ident, ".", combine=True)).setName("Column Name").addParseAction(upcaseTokens)
columnNameList = Group(delimitedList(columnName))
tableName = (delimitedList(ident, ".", combine=True)).setName("Table Name").addParseAction(upcaseTokens)
tablenameList = Group(delimitedList(tableName))

whereExpression = Forward()
and_ = Keyword("and", caseless=True)
or_ = Keyword("or", caseless=True)
in_ = Keyword("in", caseless=True)
GROUP_BY = Keyword("group by", caseless=True)
HAVING = Keyword("having", caseless=True)
CONTAINS = Keyword("contains", caseless=True)

E = CaselessLiteral("E")
binop = oneOf("= != < > >= <= eq ne lt le gt ge", caseless=True)
arithSign = Word("+-", exact=1)
realNum = Combine(Optional(arithSign) + (Word(nums) + "." + Optional (Word(nums)) or ("." + Word(nums))) + Optional(E + Optional(arithSign) + Word(nums)))
intNum = Combine(Optional(arithSign) + Word(nums) + Optional(E + Optional("+") + Word(nums)))
columnRval = realNum or intNum or quotedString or columnName
whereCondition = Group(
    (columnName + binop + columnRval) or
    (columnName + in_ + "(" + delimitedList(columnRval) + ")") or
    (columnName + in_ + "(" + selectStmt + ")") or
    ("(" + whereExpression + ")")
)
whereExpression << whereCondition + ZeroOrMore((and_ or or_) + whereExpression)

# Define the SQL grammar
selectStmt <<= (SELECT + ('*' or columnNameList)("columns") + FROM + tableNameList("tables") + Optional(Group(WHERE + whereExpression), "")("where"))
sql = selectStmt

# Run tests
if __name__ == "__main__":
    sql.runTests("""\

        # multiple tables
        SELECT * from XYZZY, ABC

        # dotted table name
        select * from SYS.XYZZY

        Select A from Sys.dual

        Select A,B,C from Sys.dual

        Select A, B, C from Sys.dual, Table2   

        # FAIL - invalid SELECT keyword
        Xelect A, B, C from Sys.dual

        # FAIL - invalid FROM keyword
        Select A, B, C frox Sys.dual

        # FAIL - incomplete statement
        Select

        # FAIL - incomplete statement
        Select * from

        # FAIL - invalid column
        Select &&& frox Sys.dual

        # where clause
        Select A from Sys.dual where a in ('RED','GREEN','BLUE')

        # compound where clause
        Select A from Sys.dual where a in ('RED','GREEN','BLUE') and b in (10,20,30)

        # where clause with comparison operator
        Select A,b from table1,table2 where table1.id eq table2.id""")