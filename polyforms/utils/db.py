import sqlite3   # enable control of an sqlite database
import hashlib   # allows for passwords and emails to be encrypted and decrypted
from flask import session  # interact with cookie
import os

#this will be the one we use when routes work
#f = "data/database.db"

#temp
local_db_location =  os.path.abspath(os.path.dirname(__file__))
global db_file
db_file = local_db_location + "/../data/database.db"
path_to_db = db_file

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
    
def add_form(user_id, formTitle, loginReq, publicReq, theme, open, message):
    db, c = open_db()
    c.execute("INSERT INTO forms (title, owner_id, login_required, public_results, theme, created, open, message) VALUES (?,?,?,?,?, datetime('now'), ?, ?)", (formTitle, user_id, loginReq, publicReq, theme, open, message))
    form_id = c.execute("SELECT max(form_id) FROM forms;").fetchone()
    close_db(db)
    return form_id[0]

def add_response(userID, formID, question_id, response, timestamp):
    db, c = open_db()
    c.execute("SELECT response_id FROM responses where form_id = " + str(formID) + ";")
    tempCounter = c.fetchall()
    if tempCounter == None or tempCounter == [] or len(tempCounter) == 0:
        response_id = 1
    else:
        response_id = len(tempCounter) + 1
    c.execute("INSERT INTO responses (response_id, form_id, question_id, user_id, response, timestamp) VALUES (?,?,?,?,?,?)", (response_id, formID, question_id, userID, response, timestamp))
    close_db(db)
    
def add_question(formID, question, type, required, min, max):
    db, c = open_db()
    c.execute("SELECT question_id FROM questions where form_id = " + str(formID) + ";")
    tempCounter = c.fetchall()
    print "tempcounter/...."
    print tempCounter
    if tempCounter == None or tempCounter == [] or len(tempCounter) == 0:
        question_id = 1
    else:
        question_id = len(tempCounter) + 1
    print question_id
    print "INSERT INTO questions (question, question_id, form_id, type, required, min, max) VALUES (?,?,?,?,?,?,?);", (question, int(question_id),int(formID), type, required, min, max)
    c.execute("INSERT INTO questions (question, question_id, form_id, type, required, min, max) VALUES (?,?,?,?,?,?,?);", (question, int(question_id),int(formID), type, required, min, max))
    db.commit()
    db.close()
    return question_id

def add_option(formID, questionID, text_user_sees, value):
    db, c = open_db()
    print "INSERT INTO options (form_id, question_id, text_user_sees, value) VALUES (?,?,?,?)", (formID, questionID, text_user_sees, value)
    c.execute("INSERT INTO options (form_id, question_id, text_user_sees, value) VALUES (?,?,?,?)", (formID, questionID, text_user_sees, value))
    close_db(db)
    
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
    formData["open"] = tempResult[7]
    #Add creator ID
    ownerID = tempResult[2]
    c.execute("SELECT username FROM accounts where user_id = " + str(ownerID) + ";")
    #print ownerID
    tempResult = c.fetchone()
    #print tempResult
    formData["owner"] = (str(tempResult[0]))
    #========================
    # headers + types
    c.execute("SELECT * FROM questions WHERE form_id = " + str(formID) + " AND type != 'section';")
    tempResult = c.fetchall()
    if tempResult is not None:
        for each in tempResult:
            #question_id_array.append(each[0])
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
    responseArray = c.execute("SELECT * FROM responses WHERE form_id = ? ORDER BY response_id, question_id;", (formID,)).fetchall()    
    if len(responseArray) > 0:
        print "======== start"
        print not responseArray
        print responseArray
        print "============ end"
        currentResponseID = responseArray[0][3]
        tempArray = []
        dataArray.append([])
        for each in responseArray:
            if each[3] == currentResponseID:
                dataArray[-1].append(each[4])
            else:
                dataArray.append([])
                currentResponseID = each[3]
                dataArray[-1].append(each[4])
        formData["data"] = dataArray
    else:
        formData["data"] = []
    close_db(db)
    return formData

#This returns a dictionary with the same syntax of returnFormDataNoResponse(formID) but with responses

def getFormDataWithResponse(formID):
    #=================
    # "Global" Holder variables
    formData = {}
    questionArray = []
    #==================
    # Top parts of Dictionary
    db, c = open_db()
    c.execute("SELECT * FROM forms WHERE form_id = " + str(formID))
    tempResult = c.fetchone()
    #print "===TEMP RESULT ==="
    #print tempResult
    #Basic form stuff
    formData["title"] = str(tempResult[1])
    formData["id"] = str(tempResult[0])
    formData["theme"] = str(tempResult[5])
    formData["open"] = tempResult[7]
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
    formData["open"] = tempResult[7]
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
def getPublicForms(number):
    formArray = []
    db, c = open_db()
    c.execute("SELECT * FROM forms WHERE login_required = 0 AND open = 1 ORDER BY created DESC;")
    tempResult = c.fetchmany(size=number)
    for each in tempResult:
        #tempDict = {}
        #tempDict["form_id"] = each[0]
        #tempDict["title"] = each[1]
        #tempDict["owner_id"] = each[2]

        #ownerID = each[2]
        #c.execute("SELECT username FROM accounts where user_id = " + str(ownerID) + ";")
        #print ownerID
        #tempResult = c.fetchone()
        #print tempResult
        #tempDict["owner"] = (str(tempResult[0]))
        #tempDict["theme"] = each[5]
        #tempDict["open"] = each[7]
        #formArray.append(tempDict)
        formArray.append(getFormData(each[0]))


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

def update_form(formID, colName, status):
    db, c = open_db()
    print "UPDATE forms SET " + "'"+ colName + "' = " + "" + str(status) + " WHERE form_id = '" + str(formID) + "';"
    c.execute("UPDATE forms SET " + "'"+ colName + "' = " + "" + str(status) + " WHERE form_id = '" + str(formID) + "';")
    print "updated formID" + str(formID)
    close_db(db)


def get_form_questionResponses(form_id, question_id):
    formDict = getFormDataWithResponse(form_id)
    question = formDict["questions"][question_id - 1]
    if question["responses"] == "" or question["responses"] == None:
        responses = []
    else:
        responses = question["responses"]
    return responses

def get_form_questionsText(form_id):
    formDict = getFormDataNoResponse(form_id)
    tempArray = formDict["questions"]
    questionArray =[]
    for each in tempArray:
        questionArray.append(each["question"])
    return questionArray
    
def get_form_questionsOptions(form_id, question_id):
    formDict = getFormDataNoResponse(form_id)
    question = formDict["questions"][question_id - 1]
    optionArray = []
    for each in question:
        optionArray.append(each["option"])
    return optionArray

#Deletes a form, questions and responses
def delete_form(form_id):
    db, c = open_db()
    c.execute("DELETE FROM forms WHERE form_id=?;", (form_id,))
    c.execute("DELETE FROM questions WHERE form_id=?;", (form_id,))
    c.execute("DELETE FROM responses WHERE form_id=?;", (form_id,))
    c.execute("DELETE FROM options WHERE form_id=?;", (form_id,))
    close_db(db)

def delete_question(form_id, question_id):
    db, c = open_db()
    # Delete the question from th DB
    c.execute("DELETE FROM questions WHERE form_id = " + str(form_id) + " AND question_id = " + str(question_id) + ";")
    c.execute("DELETE FROM responses WHERE form_id = " + str(form_id) + " AND question_id = " + str(question_id) + ";")
    c.execute("DELETE FROM options WHERE form_id = " + str(form_id) + " AND question_id = " + str(question_id) + ";")
    c.fetchall() # do this to clear / reset the cache 
    # Re-number all the existing ones
    c.execute("SELECT question_id FROM questions where form_id = " + str(form_id) + ";")
    tempCounter = c.fetchall()
    if tempCounter == 0 or tempCounter == None:
        pass
    else:
        #tempCounter = question_id + 1
        c.execute("UPDATE questions SET question_id = question_id - 1 WHERE question_id > " + str(tempCounter) + ";")
        c.execute("UPDATE responses SET question_id = question_id - 1 WHERE question_id > " + str(tempCounter) + ";")
        c.execute("UPDATE options SET question_id = question_id - 1 WHERE question_id > " + str(tempCounter) + ";")
    close_db(db)

def create_tables():
    db, c = open_db()
    c.execute("CREATE TABLE IF NOT EXISTS forms(form_id INTEGER PRIMARY KEY, title TEXT, owner_id INTEGER, login_required INTEGER, public_results INTEGER, theme TEXT, created TEXT, open INTEGER, message TEXT);")
    c.execute("CREATE TABLE IF NOT EXISTS responses(form_id INTEGER, question_id INTEGER, user_id INTEGER, response_id INTEGER, response BLOB, timestamp TEXT);")
    c.execute("CREATE TABLE IF NOT EXISTS questions(question_id INTEGER, question text, type TEXT, form_id INTEGER, required INTEGER, min INTEGER, max INTEGER, optional INTEGER);")
    c.execute("CREATE TABLE IF NOT EXISTS options(form_id INTEGER, question_id INTEGER, option_index INTEGER PRIMARY KEY, text_user_sees TEXT, value TEXT);")
    c.execute("CREATE TABLE IF NOT EXISTS accounts(user_id INTEGER PRIMARY KEY, username TEXT, password TEXT, security_question TEXT, security_question_answer TEXT);")
    #c.execute("CREATE TABLE IF NOT EXISTS styles(form_id INTEGER, row INTEGER, column INTEGER, property TEXT, value TEXT);")
    close_db(db)
    
