# CS 5300 Project 1 SQL -> relational algebra
# Luka Ivicevic and David Tutt
# Notes:
#   -   Trouble matching some single quoted strings, if test input is copy and pasted from website, 
#       the single quotes used are unicode right/left single quotation mark, if typed from my keyboard,
#       it is unicode apostrophe.
# 
#

# Imports
from pyparsing import Literal, CaselessLiteral, Word, delimitedList, Optional, \
    Combine, Group, alphas, nums, alphanums, ParseException, Forward, oneOf, quotedString, \
    ZeroOrMore, restOfLine, Keyword, upcaseTokens

# Define SQL tokens
selectStmt = Forward()
SELECT = Keyword("select", caseless=True).addParseAction(upcaseTokens)
FROM = Keyword("from", caseless=True).addParseAction(upcaseTokens)
WHERE = Keyword("where", caseless=True).addParseAction(upcaseTokens)
AS = Keyword("as", caseless=True).addParseAction(upcaseTokens)
UNION = Keyword("union", caseless=True).addParseAction(upcaseTokens)
INTERSECT = Keyword("intersect", caseless=True).addParseAction(upcaseTokens)
EXCEPT = Keyword("except", caseless=True).addParseAction(upcaseTokens)
COUNT = Keyword("count", caseless=True).addParseAction(upcaseTokens)
MAX = Keyword("max", caseless=True).addParseAction(upcaseTokens)
AVG = Keyword("avg", caseless=True).addParseAction(upcaseTokens)
SUM = Keyword("sum", caseless=True).addParseAction(upcaseTokens)

ident = Word( alphas, alphanums + "_$" ).setName("identifier")
columnName = ( delimitedList( ident, ".", combine=True ) ).setName("column name").addParseAction(upcaseTokens)
columnNameList = Group( delimitedList( columnName ))
tableName = ( delimitedList( ident, ".", combine=True ) ).setName("table name").addParseAction(upcaseTokens)
tableNameAs = ( delimitedList( ident + " " + AS + " " + ident, ",", combine=True ) ).setName("table name").addParseAction(upcaseTokens)
tableNameList = delimitedList( tableName )
funcs = ((COUNT | MAX | AVG | SUM) + "(" + ( "*" | columnName ) + ")")

whereExpression = Forward()
and_ = Keyword("and", caseless=True).addParseAction(upcaseTokens)
or_ = Keyword("or", caseless=True).addParseAction(upcaseTokens)
in_ = Keyword("in", caseless=True).addParseAction(upcaseTokens)
GROUP_BY = Keyword("group by", caseless=True).addParseAction(upcaseTokens)
HAVING = Keyword("having", caseless=True).addParseAction(upcaseTokens)
CONTAINS = Keyword("contains", caseless=True).addParseAction(upcaseTokens)

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
    ( funcs + binop + columnRval ) |
    ( columnName + binop + columnRval ) |
    ( columnName + in_ + "(" + delimitedList( columnRval ) + ")" ) |
    ( columnName + in_ + "(" + selectStmt + ")" ) |
    ( "(" + whereExpression + ")" )
    )
whereExpression << whereCondition + Optional(Group(GROUP_BY + columnName + Optional(HAVING + Group((funcs + binop + columnRval) | (columnName + binop + columnRval)) + ZeroOrMore(( and_ | or_ ) + Group( (funcs + binop + columnRval) | (columnName + binop + columnRval)))))) + ZeroOrMore( ( and_ | or_ ) + whereExpression )

# Define the SQL grammar
selectStmt <<= (SELECT + ('*' | Group(delimitedList(Group( (funcs | columnName ) + Optional(AS + ident)))))("columns") + \
                FROM + Group(delimitedList(Group(tableName + Optional(AS + ident))))( "tables" ) + \
                Optional(Group(WHERE + whereExpression), "")("where")) + \
                Optional((UNION + selectStmt)("union") | (INTERSECT + selectStmt)("intersect") | (EXCEPT + selectStmt)("except") | (CONTAINS + selectStmt)("contains")) 

SQLParser = selectStmt # TODO - make paranthesies optional around a selectStmt (test h)

# Tests
if __name__ == "__main__":
    test = "SELECT sid, sname as s, max(rating), E FROM Sailors as T, Boats WHERE count(r) = 2 and S2.rating = 10 GROUP BY D.sdf Having count(d) > 5 or max(R) = 5"
    try:
        #print(test, "\n-----\n", SQLParser.parseString(test))
        parsedQuery = SQLParser.parseString(test)
    except Exception as e:
        print("Syntax Error parsing: " + test)
        print(e)
    
    # List of tables being used
    tables = parsedQuery[3]
    # attributes: list of attributes and their type (comes after select)
    attributes = parsedQuery[1]

    # Define the schema
    sailors = (
        ("tname", "sailors"),
        ("sid", "int"),
        ("sname", "str"),
        ("rating", "int"),
        ("age", "real")
    )
    boats = (
        ("tname", "boats"),
        ("bid", "int"),
        ("bname", "str"),
        ("color", "str")
    )
    reserves = (
        ("tname", "reserves"),
        ("sid", "int"),
        ("bid", "int"),
        ("day", "date")
    )

    # Check if the table used in the query are valid based on the schema
    for item in tables:
        if (str(item[0]).upper() != sailors[0][1].upper()) and (str(item[0]).upper() != reserves[0][1].upper()) and (str(item[0]).upper() != boats[0][1].upper()):
            print(item[0] + " is not a table in the schema.")
            # Do something since a table is invalid
    
    # Check if the select attributes are valid according to the schema and what tables are being used in the query
    # - Iterate through each attributes
    # - Check if it's a built-in function, if it is then get the 2 index (that will be the attribute)
    # - If it's not a build in function, then get the 0 index (that will be the attribute)
    # - Check if that attribute is in any of the tables
    # - If it is, make sure that table is being used in the query (check if the table is in 'tables')
    attrTablePairs = []
    for attribute in attributes:
        # Extract the correct attribute
        if (str(attribute[0]).upper() == "COUNT") or (str(attribute[0]).upper() == "MAX") or (str(attribute[0]).upper() == "AVG") or (str(attribute[0]).upper() == "SUM"):
            attr = attribute[2]
        else:
            attr = attribute[0]
        # Check if the attribute is in any of the tables in the schema
        isInTable = False
        attrTableName = ""
        for item in sailors:
            if (item[0].upper() == attr):
                isInTable = True
                attrTableName = "SAILORS"
                break
        for item in boats:
            if (item[0].upper() == attr):
                isInTable = True
                attrTableName = "BOATS"
                break
        for item in reserves:
            if (item[0].upper() == attr):
                isInTable = True
                attrTableName = "RESERVES"
                break
        if (isInTable == False):
            print(attr + " is not an attribute in the schema.")
            # Do something since an attribute is invalid
        else:
            print(attr + " is in the table " + attrTableName)
            # Build list of attr, table pairs
            attrTablePairs.append((attr, attrTableName))
    print(attrTablePairs)
