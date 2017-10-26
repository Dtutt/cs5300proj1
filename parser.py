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


def sqlparse(sql):
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

    ident = Word(alphas, alphanums + "_$").setName("identifier")
    columnName = (delimitedList(ident, ".", combine=True)).setName("column name").addParseAction(upcaseTokens)
    columnNameList = Group(delimitedList(columnName))
    tableName = (delimitedList(ident, ".", combine=True)).setName("table name").addParseAction(upcaseTokens)
    tableNameAs = (delimitedList(ident + " " + AS + " " + ident, ",", combine=True)).setName(
        "table name").addParseAction(upcaseTokens)
    tableNameList = delimitedList(tableName)
    funcs = ((COUNT | MAX | AVG | SUM) + "(" + ("*" | columnName) + ")")

    whereExpression = Forward()
    and_ = Keyword("and", caseless=True).addParseAction(upcaseTokens)
    or_ = Keyword("or", caseless=True).addParseAction(upcaseTokens)
    in_ = Keyword("in", caseless=True).addParseAction(upcaseTokens)
    GROUP_BY = Keyword("group by", caseless=True).addParseAction(upcaseTokens)
    HAVING = Keyword("having", caseless=True).addParseAction(upcaseTokens)
    CONTAINS = Keyword("contains", caseless=True).addParseAction(upcaseTokens)

    E = CaselessLiteral("E")
    binop = oneOf("= != < > >= <= eq ne lt le gt ge", caseless=True)
    arithSign = Word("+-", exact=1)
    realNum = Combine(Optional(arithSign) + (Word(nums) + "." + Optional(Word(nums)) |
                                             ("." + Word(nums))) +
                      Optional(E + Optional(arithSign) + Word(nums)))
    intNum = Combine(Optional(arithSign) + Word(nums) +
                     Optional(E + Optional("+") + Word(nums)))

    columnRval = realNum | intNum | quotedString | columnName
    whereCondition = Group(
        (funcs + binop + columnRval) |
        (columnName + binop + columnRval) |
        (columnName + in_ + "(" + delimitedList(columnRval) + ")") |
        (columnName + in_ + "(" + selectStmt + ")") |
        ("(" + whereExpression + ")")
    )
    whereExpression << whereCondition + Optional(Group(GROUP_BY + columnName + Optional(
        HAVING + Group((funcs + binop + columnRval) | (columnName + binop + columnRval)) + ZeroOrMore(
            (and_ | or_) + Group((funcs + binop + columnRval) | (columnName + binop + columnRval)))))) + ZeroOrMore(
        (and_ | or_) + whereExpression)

    # Define the SQL grammar
    selectStmt <<= (SELECT + ('*' | Group(delimitedList(Group((funcs | columnName) + Optional(AS + ident)))))(
        "columns") + \
                    FROM + Group(delimitedList(Group(tableName + Optional(AS + ident))))("tables") + \
                    Optional(Group(WHERE + whereExpression), "")("where")) + \
                   Optional(
                       (UNION + selectStmt)("union") | (INTERSECT + selectStmt)("intersect") | (EXCEPT + selectStmt)(
                           "except") | (CONTAINS + selectStmt)("contains"))

    SQLParser = selectStmt  # TODO - make paranthesies optional around a selectStmt (test h)

    # Begin validation

    test = "SELECT sid, sname as s, max(rating), E FROM Sailors as T, Boats WHERE count(sid) = 2 and S2.rating = 10 and sid = 4 GROUP BY sid Having count(d) > 5 or max(R) = 5"
    try:
        print(sql, "\n-----\n", SQLParser.parseString(sql), "\n")
        parsedQuery = SQLParser.parseString(sql)
    except Exception as e:
        print("Syntax Error parsing: " + sql)
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
        if (str(item[0]).upper() != sailors[0][1].upper()) and (
            str(item[0]).upper() != reserves[0][1].upper()) and (str(item[0]).upper() != boats[0][1].upper()):
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
        if (str(attribute[0]).upper() == "COUNT") or (str(attribute[0]).upper() == "MAX") or (
            str(attribute[0]).upper() == "AVG") or (str(attribute[0]).upper() == "SUM"):
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

    # Check to see if the corresponding table is being used in the query
    for pair in attrTablePairs:
        beingUsed = False
        for table in tables:
            if (pair[1] == str(table[0].upper())):
                beingUsed = True
                break
        if (beingUsed == False):
            # Attribute is invalid as the table is belongs to is not being used in the query
            print(str(pair[0]) + " is invalid as the table it belongs to (" + str(
                pair[1]) + ") is not being used in the query.")

    # Check if the attributes being used in the WHERE stmnt are valid
    # - Check if WHERE stmnt exists
    if (len(parsedQuery) >= 5):
        whereExp = parsedQuery[4]
        for exp in whereExp:
            if (exp != "WHERE" and exp != "AND" and exp != "OR"):
                if (exp[0] == "GROUP BY"):
                    valid = False
                    for attr in attrTablePairs:
                        if (str(exp[1]).upper() == str(attr[0]).upper()):
                            valid = True
                            break
                    if (valid == False):
                        print(exp[1] + " in the group by clause is not a valid attribute")
                    if (len(exp) >= 3):
                        if (str(exp[2]).upper() == "HAVING"):
                            print("")
                else:
                    if (exp[0] == "COUNT" or exp[0] == "MAX" or exp[0] == "AVG" or exp[0] == "SUM"):
                        # Check if the attribute is valid
                        valid = False
                        for attr in attrTablePairs:
                            if (str(exp[2]).upper() == str(attr[0]).upper()):
                                valid = True
                                break
                        if (valid == False):
                            print(exp[2] + " in the where clause is not a valid attribute")
                    elif ("." in exp[0]):
                        # Check if the attribute is valid
                        valid = False
                        for attr in attrTablePairs:
                            if (str(exp[0]).split(".")[1] == str(attr[0].upper())):
                                valid = True
                                break
                        if (valid == False):
                            print(exp[0] + " in the where clause is not a valid attribute")
                    else:
                        # Check if the attribute is valid
                        valid = False
                        for attr in attrTablePairs:
                            if (str(exp[0].upper()) == str(attr[0]).upper()):
                                valid = True
                                break
                        if (valid == False):
                            print(exp[0] + " in the where clause is not a valid attribute")

    # RELATIONAL ALGEBRA TRANSLATION
    Aggfunc=['COUNT','MAX','MAX','AVG','SUM']
    Aggfunc2=['GROUP BY',"HAVING"]
    #SELECT conversion
    #Create Regular Expression string
    Rastr='[(Projection)'

    #first element of section
    first=True
    rename=False
    for column in parsedQuery[1]:
        if first:
            if str(column[0]) in Aggfunc:
                Rastr=Rastr+str(column[0])+'('+str(column[2])+')'
            else:
                Rastr=Rastr+str(column[0])
            first = False
        else:
            if str(column[0]) in Aggfunc:
                Rastr=Rastr+','+str(column[0])+'('+str(column[2])+')'
            else:
                Rastr=Rastr+','+str(column[0])

        # Rename Set
        if column.__len__() > 1:
            if str(column[1])=='AS':
                if rename:
                    rename=renastr+','+str(column[2])
                else:
                    renastr="(Rename)"+"["+str(column[2])+'<-'+str(column[0])+','
                    rename=True

    Rastr=renastr+"]"+Rastr

    #WHERE conversion
    for attr in whereExp:
        aggfunc1=False
        aggfunc2=False
        if str(attr)=="AND" or str(attr)=='OR':
            Rastr=Rastr+str(attr)+" "
        elif str(attr)=="WHERE":
            Rastr = Rastr + '](Select)['
        else:
            for item in attr:
                if item in Aggfunc:
                    Rastr = Rastr + str(attr[0]) + '(' + str(attr[2]) + ')' + ' = ' + str(attr[5]) + ' '
                    aggfunc1=True
                elif str(item) in Aggfunc2:
                    Rastr = Rastr + str(item) + '('
                    aggfunc2=True
                else:
                    if aggfunc2:
                        if item[0] in Aggfunc:
                            Rastr = Rastr + str(item[0]) + '(' + str(item[2]) + ')' + '=' + str(item[5]) + ' '
                        elif str(item)=="AND" or str(item)=="OR":
                            Rastr = Rastr + str(item)+" "
                        else:
                            Rastr=Rastr+str(item)+') '
                    elif not aggfunc1:
                        Rastr = Rastr + str(item)+' '
            if aggfunc2:
                Rastr=Rastr+')'
    Rastr=Rastr+']'
    #FROM conversion
    Rastr = Rastr+'['
    first = True
    for table in tables:
        if first:
            if table.__len__()==1:
                Rastr=Rastr+str(table)
            else:
                Rastr=Rastr+'(Rename)['+table[2]+']'+str(table[0])
            first=False
        else:
            if table.__len__()==1:
                Rastr = Rastr + ' x ' + str(table)
            else:
                Rastr=Rastr+'x (Rename)['+table[2]+']'+str(table[0])

    Rastr = Rastr + ']'
    print(Rastr)
    return Rastr

