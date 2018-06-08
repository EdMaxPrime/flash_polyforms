import sqlite3   # enable control of an sqlite database
import hashlib   # allows for passwords and emails to be encrypted and decrypted
from flask import session   # interact with cookie

#this will be the one we use when routes work
#f = "data/database.db"

#temp
local_db_location = "data/database.db"
path_to_db = local_db_location

def use_database(path):
    if len(path) > 0 and path[-1] != "/":
        path += "/"
    path_to_db = path + local_db_location

def open_db():
    db = sqlite3.connect(path_to_db) # open if f exists, otherwise create
    c = db.cursor()                  # facilitate db ops
    return db, c

def close_db(db):
    db.commit()
    db.close()

# helper function for incrementing id numbers
# returns next id number to be used
def increment_id(table):
    db, c = open_db()
    command = "SELECT * FROM %s" % (table)
    id = 0
    for entry in c.execute(command):
        id+=1
    close_db(db)
    return id

def hashed(foo):
    return hashlib.md5(str(foo)).hexdigest()
    
def add_form(user_id, formTitle, loginReq, publicReq, theme):
    db, c = open_db()
    c.execute("INSERT INTO forms (title, owner_id, login_required, public_results, theme, created) VALUES (?,?,?,?,?, datetime('now'))", (formTitle, user_id, loginReq, publicReq, theme))
    form_id = c.execute("SELECT max(form_id) FROM forms;").fetchone()
    close_db(db)
    return form_id[0]

def add_response(userID, formID, question_id, response, timestamp):
    db, c = open_db()
    c.execute("INSERT INTO responses (form_id, question_id, user_id, response, timestamp) VALUES (?,?,?,?,?)", (formID, question_id, userID, response, timestamp))
    close_db(db)
    
def add_question(formID, question, type, required, min, max):
    db, c = open_db()
    c.execute("INSERT INTO questions (question, form_id, type, required, min, max) VALUES (?,?,?,?,?,?);", (question, int(formID), type, required, min, max))
    db.commit()
    db.close()

def add_option(formID, questionID, text_user_sees, value):
    db, c = open_db()
    c.execute("INSERT INTO options (form_id, question_id, text_user_sees, value) VALUES (?,?,?,?)", (formID, questionID, text_user_sees, value))
    db.commit()
    db.close()
    
def add_style(formID, row, column, property, value):
    db, c = open_db()
    c.execute("INSERT INTO styles (form_id, row, column, property, value) VALUES (?,?,?,?,?)", (formID, row, column, property, value))
    db.commit()
    db.close()

# add security questions later
# sqlite automatically increments all integer primary keys (user_id)
def add_account(username, password, security_question, security_question_answer):
    db, c = open_db()
    c.execute("INSERT INTO accounts (username, password, security_question, security_question_answer) VALUES ('%s', '%s', '%s', '%s')" % (username, hashed(password), str(security_question), hashed(str(username) + str(security_question_answer))))
    close_db(db)

#Returns true if this username+password pair matches, false if it does not
def validate_login(username, password):
    db, c = open_db()
    #print  "SELECT username FROM accounts WHERE username" + " = '" + str(username) + "' AND password = '" + str(hashed(password)) + "';"
    c.execute("SELECT username FROM accounts WHERE username" + " = '" + str(username) + "' AND password = '" + str(hashed(password)) + "';")
    results = c.fetchone()
    close_db(db)
    #print results
    if results == None:
        return False
    else:
        return len(results) > 0

#Returns true if this username+password pair matches, false if it does not
def validate_resetPassword(username, security_question, security_question_answer):
    db, c = open_db()
    c.execute("SELECT username FROM accounts WHERE username" + " = '" + str(username) + "' AND security_question = '" + str(security_question) +"' AND security_question_answer = '" + str(hashed(str(username) + str(security_question_answer))) + "';")
    results = c.fetchone()
    close_db(db)
    if results == None:
        return False
    else:
        return len(results) > 0

#Checks if something exists in a specific Column within a table. Returns true if it is found
def checkExist(table, colName, query):
    db, c = open_db()
    #print "SELECT " + str(colName) + " FROM " + table + " WHERE " + colName + "=" + query +";"
    c.execute("SELECT " + str(colName) + " FROM " + str(table) + " WHERE " + str(colName) + " = '" + str(query) +"';")
    results = c.fetchone()
    close_db(db)
    if results == None:
        return False
    else:
        return len(results) > 0

#Returns true if this username is already taken, false otherwise
def user_exists(username):
    db, c = open_db()
    c.execute("SELECT username FROM accounts WHERE username = '%s';" % (username,)) #comma needed for this
    results = c.fetchone()
    close_db(db)
    if results == None:
        return False
    else:
        return len(results) > 0

#returns the ID # for a specific form / question / user based off 1 thing you know about a column in the Table + the colName of the ID
def getID(tableName, idCol, queryCol, query):
    db, c = open_db()
    c.execute("SELECT " + str(idCol) + " FROM " + str(tableName) + " WHERE " + str(queryCol) + " = '%s';" % (query,)) #comma needed for this
    ID = c.fetchone()
    close_db(db)
    return ID[0]

# This returns a dictionary that represents a form.
# Keys are title, id, created, headers, types, data.
# Header is an array of questions.
# Types is an array of what types of question each question is
# Data is a 2d Array that holds the arrays of responses per question
def getFormData(formID):
    #=================
    # "Global" Holder variables
    formData = {}
    headerArray = []
    typeArray = []
    dataArray = []
    #==================
    # Top parts of Dictionary
    db, c = open_db()
    c.execute("SELECT * FROM forms WHERE form_id = " + str(formID))
    tempResult = c.fetchone()
    #Basic form stuff
    formData["title"] = str(tempResult[1])
    formData["id"] = str(tempResult[0])
    formData["created"] = str(tempResult[6])
    formData["login_required"] = str(tempResult[3])
    formData["public_results"] = str(tempResult[4])
    #Add creator ID
    ownerID = tempResult[2]
    c.execute("SELECT username FROM accounts where user_id = " + str(ownerID) + ";")
    #print ownerID
    tempResult = c.fetchone()
    #print tempResult
    formData["owner"] = (str(tempResult[0]))
    #========================
    # headers + types
    question_id_array = []
    c.execute("SELECT * FROM questions WHERE form_id = " + str(formID) + ";")
    tempResult = c.fetchall()
    if tempResult is not None:
        for each in tempResult:
            question_id_array.append(each[0])
            headerArray.append(str(each[1]))
            typeArray.append(str(each[2]))
        formData["headers"] = headerArray
        formData["types"] = typeArray
    if tempResult == None:
        question_id_array = None
        formData["headers"] = None
        formData["types"] = None
    #========================
    # DATA 
    tempArray = []
    if question_id_array is not None:
        for questionID in question_id_array:
            c.execute("SELECT * FROM responses WHERE question_id = " + str(questionID) + ";")
            tempResult = c.fetchall()
            for each in tempResult:
                tempArray.append(each[4])
            dataArray.append(tempArray)
        formData["data"] = dataArray
    else:
        formData["data"] = None
    close_db(db)
    return formData
'''
This returns a dictionary with the same syntax of returnFormDataNoResponse(formID) but with responses

def getFormData(formID):
    #=================
    # "Global" Holder variables
    formData = {}
    questionArray = []
    #==================
    # Top parts of Dictionary
    db, c = open_db()
    c.execute("SELECT * FROM forms WHERE form_id = " + str(formID))
    tempResult = c.fetchone()
    #Basic form stuff
    formData["title"] = str(tempResult[1])
    formData["id"] = str(tempResult[0])
    formData["theme"] = str(tempResult[5])
    #Add creator ID
    ownerID = tempResult[2]
    c.execute("SELECT username FROM accounts where user_id = " + str(ownerID) + ";")
    #print ownerID
    tempResult = c.fetchone()
    #print tempResult
    formData["owner"] = (str(tempResult[0]))
    #========================
    # questions
    c.execute("SELECT * FROM questions WHERE form_id = " + str(formID) + ";")
    tempResult = c.fetchall()
    for each in tempResult:
        tempDict = {}
        optionArray = []
        responseArray = []
        tempDict["question_id"] = each[0]
        tempDict["question"] = str(each[1])
        tempDict["type"] = str(each[2])
        tempDict["min"] = each[4]
        tempDict["max"] = each[5]

        c.execute("SELECT * from options WHERE question_id = " + str(each[0]) + ";")
        optionDump = c.fetchall()
        if optionDump is not None:
            for eachOption in optionDump:
                tempOptionDict = {}
                tempOptionDict["text"] = str(eachOption[3])
                tempOptionDict["value"] = str(eachOption[4])
                optionArray.append(tempOptionDict)
            tempDict["option"] = optionArray
        if optionDump == None:
            tempDict["option"] = None

        #===
        c.execute("SELECT * from responses WHERE question_id = " + str(each[0]) + ";")
        responseDump = c.fetchall()
        if responseDump is not None:
            for eachResponse in responseDump:
                responseArray.append(str(eachResponse[4]))
            tempDict["response"] = responseArray
        if responseDump == None:
            tempDict["response"] = None
        #===
        questionArray.append(tempDict)

    formData["questions"] = questionArray
    close_db(db)
    return formData
'''

# Returns a dictionary for the from
# First layer of keys are title, id, theme, owner, and questions
# The "Question" key is an array of dictionaries with each dictionary being a question
#   Each dictionary has the keys: question_id, question, type max, and options
#   Options is an array of dictionaries, each dictionary representing an option for the question
#       These dictionaries have keys, text and values. 
def getFormDataNoResponse(formID):
    #=================
    # "Global" Holder variables
    formData = {}
    questionArray = []
    #==================
    # Top parts of Dictionary
    db, c = open_db()
    c.execute("SELECT * FROM forms WHERE form_id = " + str(formID))
    tempResult = c.fetchone()
    #Basic form stuff
    formData["id"] = str(tempResult[0])
    formData["title"] = str(tempResult[1])
    formData["login_required"] = str(tempResult[3])
    formData["public_results"] = str(tempResult[4])
    formData["theme"] = str(tempResult[5])
    #Add creator ID
    ownerID = tempResult[2]
    c.execute("SELECT username FROM accounts where user_id = " + str(ownerID) + ";")
    #print ownerID
    tempResult = c.fetchone()
    #print tempResult
    formData["owner"] = (str(tempResult[0]))
    #========================
    # questions
    c.execute("SELECT * FROM questions WHERE form_id = " + str(formID) + ";")
    tempResult = c.fetchall()
    for each in tempResult:
        tempDict = {}
        optionArray = []
        tempDict["question_id"] = each[0]
        tempDict["question"] = each[1]
        tempDict["type"] = each[2]
        tempDict["min"] = each[4]
        tempDict["max"] = each[5]

        c.execute("SELECT * from options WHERE question_id = " + str(each[0]) + ";")
        optionDump = c.fetchall()
        if optionDump is not None:
            for eachOption in optionDump:
                tempOptionDict = {}
                tempOptionDict["text"] = eachOption[3]
                tempOptionDict["value"] = eachOption[4]
                optionArray.append(tempOptionDict)
            tempDict["option"] = optionArray
        else:
            tempDict["option"] = None
        questionArray.append(tempDict)
    formData["questions"] = questionArray
    close_db(db)
    return formData

# This returns an array of Dictionaries. Each dictionary represents a form.
# Dictionary keys are: form_id, title, owner_id, owner, theme
def getPublicForms():
    formArray = []
    db, c = open_db()
    c.execute("SELECT * FROM forms WHERE login_required = 0 ORDER BY created DESC;")
    tempResult = c.fetchmany(size=24)
    for each in tempResult:
        tempDict = {}
        tempDict["form_id"] = each[0]
        tempDict["title"] = each[1]
        tempDict["owner_id"] = each[2]

        ownerID = each[2]
        c.execute("SELECT username FROM accounts where user_id = " + str(ownerID) + ";")
        #print ownerID
        tempResult = c.fetchone()
        #print tempResult
        tempDict["owner"] = (str(tempResult[0]))
        tempDict["theme"] = each[5]
        formArray.append(tempDict)


    #c.execute("INSERT INTO forms (title, owner_id, login_required, public_results, theme, created) VALUES ('form 3',1,0,0,'no theme', datetime('now'));")
    close_db(db)
    return formArray

def getSQ(username):
    db, c = open_db()
    c.execute("SELECT security_question FROM accounts WHERE username = " + "'" + str(username) + "';")
    tempResult = c.fetchone()[0]
    close_db(db)
    return str(tempResult)

def update_account(username, password):
    db, c = open_db()
    c.execute("UPDATE accounts SET password = " + "'" + str(hashed(password)) + "' WHERE username = '" + str(username) + "';")
    close_db(db)


def get_form_responses(form_id):
    return {}

def create_tables():
    db, c = open_db()
    c.execute("CREATE TABLE IF NOT EXISTS forms(form_id INTEGER PRIMARY KEY, title TEXT, owner_id INTEGER, login_required INTEGER, public_results INTEGER, theme TEXT, created TEXT);")
    c.execute("CREATE TABLE IF NOT EXISTS responses(form_id INTEGER, question_id INTEGER, user_id INTEGER, response_id INTEGER, response BLOB, timestamp TEXT);")
    c.execute("CREATE TABLE IF NOT EXISTS questions(question_id INTEGER, question text, type TEXT, form_id INTEGER, required INTEGER, min INTEGER, max INTEGER);")
    c.execute("CREATE TABLE IF NOT EXISTS options(form_id INTEGER, question_id INTEGER, option_index INTEGER PRIMARY KEY, text_user_sees TEXT, value TEXT);")
    c.execute("CREATE TABLE IF NOT EXISTS accounts(user_id INTEGER PRIMARY KEY, username TEXT, password TEXT, security_question TEXT, security_question_answer TEXT);")
    c.execute("CREATE TABLE IF NOT EXISTS styles(form_id INTEGER, row INTEGER, column INTEGER, property TEXT, value TEXT);")
    close_db(db)
    
